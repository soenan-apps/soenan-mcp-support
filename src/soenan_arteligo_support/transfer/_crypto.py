from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import BinaryIO

from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ..e2ee._core import CryptoCore
from ..e2ee._crypto import E2eeError

CHUNK_SIZE = 8 * 1024 * 1024


class EncryptionContractError(ValueError):
    """A file frame does not match its authenticated metadata."""


@dataclass(frozen=True)
class EncryptionPlan:
    locator: domain.ObjectLocator
    core: CryptoCore

    @property
    def chunks(self):
        return self.locator.descriptor.chunks

    @property
    def plaintext_size(self):
        return sum(chunk.frame.plaintext_length for chunk in self.chunks)

    def seal_chunk(self, plaintext: bytes, index: int) -> bytes:
        expected = self.chunks[index].frame
        if len(plaintext) != expected.plaintext_length:
            raise E2eeError("source_changed")
        state = crypto.StreamState()
        state.CopyFrom(self.locator.stream)
        state.next_index = index
        sealed = self.core.execute_utility(
            crypto.CoreUtilityRequest(
                seal_stream=crypto.StreamSeal(
                    state=state, plaintext=plaintext, final_frame=expected.final_frame
                )
            )
        ).stream_sealed
        frame = sealed.frame
        if frame.sha256 != expected.sha256:
            raise E2eeError("source_changed")
        return frame.ciphertext

    def open_chunk(self, ciphertext: bytes, index: int) -> bytes:
        expected = self.chunks[index].frame
        if len(ciphertext) != expected.plaintext_length + 16:
            raise EncryptionContractError(
                "ciphertext chunk size does not match manifest"
            )
        frame = crypto.StreamFrame()
        frame.CopyFrom(expected)
        frame.ciphertext = ciphertext
        state = crypto.StreamState()
        state.CopyFrom(self.locator.stream)
        state.next_index = index
        try:
            return self.core.execute_utility(
                crypto.CoreUtilityRequest(
                    open_stream=crypto.StreamOpen(
                        state=state,
                        frame=frame,
                        binding=self.locator.descriptor.exact_source_binding,
                    )
                )
            ).stream_opened.plaintext
        except E2eeError:
            raise EncryptionContractError("ciphertext authentication failed") from None


def build_encryption_plan(
    stream: BinaryIO,
    *,
    core: CryptoCore,
    object_id: str,
    binding: bytes,
    plaintext_size: int,
) -> EncryptionPlan:
    if plaintext_size <= 0:
        raise E2eeError("file_size_invalid")
    start = stream.tell()
    locator = domain.ObjectLocator(
        descriptor=domain.ObjectDescriptor(
            object_id=object_id, exact_source_binding=binding, chunk_size=CHUNK_SIZE
        )
    )
    state = None
    plaintext_offset = ciphertext_offset = 0
    count = (plaintext_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    for index in range(count):
        length = min(CHUNK_SIZE, plaintext_size - plaintext_offset)
        clear = stream.read(length)
        if len(clear) != length:
            raise E2eeError("source_changed")
        seal = crypto.StreamSeal(
            plaintext=clear, final_frame=index + 1 == count, binding=binding
        )
        if state is not None:
            seal.state.CopyFrom(state)
        sealed = core.execute_utility(
            crypto.CoreUtilityRequest(seal_stream=seal)
        ).stream_sealed
        state = sealed.state
        if index == 0:
            locator.stream.CopyFrom(state)
            locator.stream.next_index = 0
            locator.stream.finished = False
        frame = crypto.StreamFrame()
        frame.CopyFrom(sealed.frame)
        ciphertext_length = len(frame.ciphertext)
        frame.ClearField("ciphertext")
        locator.descriptor.chunks.add(
            index=index,
            plaintext_offset=plaintext_offset,
            ciphertext_offset=ciphertext_offset,
            ciphertext_size=ciphertext_length,
            frame=frame,
        )
        plaintext_offset += length
        ciphertext_offset += ciphertext_length
    if stream.read(1):
        raise E2eeError("source_changed")
    locator.descriptor.ciphertext_size = ciphertext_offset
    stream.seek(start)
    return EncryptionPlan(locator, core)


def authenticate_source(stream: BinaryIO, plan: EncryptionPlan) -> bytes:
    digest = sha256()
    start = stream.tell()
    for chunk in plan.chunks:
        clear = stream.read(chunk.frame.plaintext_length)
        plan.seal_chunk(clear, chunk.index)
        digest.update(clear)
    if stream.read(1):
        raise E2eeError("source_changed")
    stream.seek(start)
    return digest.digest()
