from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import BinaryIO

from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto
from soenan.arteligo.domain.v1 import domain_pb2 as domain

from ..e2ee._core import CryptoCore
from ..e2ee._crypto import E2eeError

CHUNK_SIZE = 8 * 1024 * 1024
_MAX_PARTS = 10_000
_MAX_OBJECT_SIZE = 5 * 1024**4
_TAG_SIZE = 16


def _frames_per_part(frame_count: int) -> int:
    return (frame_count + _MAX_PARTS - 1) // _MAX_PARTS


class EncryptionContractError(ValueError):
    """A file frame does not match its authenticated metadata."""


@dataclass(frozen=True)
class EncryptionPlan:
    locator: domain.ObjectLocator
    core: CryptoCore

    @property
    def chunks(self):
        return self.locator.descriptor.chunks

    def _seal_verified_chunk(self, plaintext: bytes, index: int) -> bytes:
        expected = self.chunks[index].frame
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

    def open_frames(self, read: Callable[[int], bytes]) -> Iterator[bytes]:
        count = len(self.chunks)
        if count == 0:
            raise EncryptionContractError("ciphertext manifest is empty")
        for index, chunk in enumerate(self.chunks):
            frame = chunk.frame
            length = chunk.ciphertext_size
            if (
                chunk.index != index
                or frame.final_frame != (index + 1 == count)
                or not 0 < frame.plaintext_length <= CHUNK_SIZE
                or length != frame.plaintext_length + _TAG_SIZE
            ):
                raise EncryptionContractError("invalid ciphertext frame manifest")
            ciphertext = read(length)
            if len(ciphertext) != length:
                raise EncryptionContractError("ciphertext frame is incomplete")
            yield self._open_chunk(ciphertext, index)

    def _open_chunk(self, ciphertext: bytes, index: int) -> bytes:
        expected = self.chunks[index].frame
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


@dataclass(frozen=True)
class PreparedUpload:
    plan: EncryptionPlan
    parts: list[domain.UploadPart]
    plaintext_sha256: bytes


def prepare_upload(
    stream: BinaryIO,
    spool: BinaryIO,
    *,
    core: CryptoCore,
    object_id: str,
    binding: bytes,
    plaintext_size: int,
) -> PreparedUpload:
    count = (plaintext_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    if plaintext_size <= 0 or plaintext_size + count * _TAG_SIZE > _MAX_OBJECT_SIZE:
        raise E2eeError("file_size_invalid")
    frames_per_part = _frames_per_part(count)
    start = stream.tell()
    locator = domain.ObjectLocator(
        descriptor=domain.ObjectDescriptor(
            object_id=object_id, exact_source_binding=binding, chunk_size=CHUNK_SIZE
        )
    )
    state = None
    plaintext_offset = ciphertext_offset = 0
    parts: list[domain.UploadPart] = []
    plaintext_digest = sha256()
    part_digest = sha256() if frames_per_part > 1 else None
    part_length = 0
    for index in range(count):
        length = min(CHUNK_SIZE, plaintext_size - plaintext_offset)
        clear = stream.read(length)
        if len(clear) != length:
            raise E2eeError("source_changed")
        plaintext_digest.update(clear)
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
        sealed_frame = sealed.frame
        ciphertext = sealed_frame.ciphertext
        ciphertext_length = len(ciphertext)
        spool.write(ciphertext)
        if part_digest is not None:
            part_digest.update(ciphertext)
        part_length += ciphertext_length
        frame = crypto.StreamFrame(
            index=sealed_frame.index,
            final_frame=sealed_frame.final_frame,
            plaintext_length=sealed_frame.plaintext_length,
            sha256=sealed_frame.sha256,
        )
        locator.descriptor.chunks.add(
            index=index,
            plaintext_offset=plaintext_offset,
            ciphertext_offset=ciphertext_offset,
            ciphertext_size=ciphertext_length,
            frame=frame,
        )
        plaintext_offset += length
        ciphertext_offset += ciphertext_length
        if (index + 1) % frames_per_part == 0 or index + 1 == count:
            parts.append(
                domain.UploadPart(
                    ciphertext_size=part_length,
                    sha256=(
                        part_digest.digest()
                        if part_digest is not None
                        else sealed_frame.sha256
                    ),
                )
            )
            if part_digest is not None:
                part_digest = sha256()
            part_length = 0
    if stream.read(1):
        raise E2eeError("source_changed")
    locator.descriptor.ciphertext_size = ciphertext_offset
    stream.seek(start)
    return PreparedUpload(
        EncryptionPlan(locator, core), parts, plaintext_digest.digest()
    )


def restore_missing_parts(
    stream: BinaryIO,
    spool: BinaryIO,
    plan: EncryptionPlan,
    parts: Sequence[domain.UploadPart],
    missing: Sequence[int],
    plaintext_sha256: bytes,
) -> None:
    start = stream.tell()
    digest = sha256()
    frames_per_part = _frames_per_part(len(plan.chunks))
    needed = set(missing)
    frame_digests: list[bytes | None] = []
    for index, chunk in enumerate(plan.chunks):
        if not 0 < chunk.frame.plaintext_length <= CHUNK_SIZE:
            raise E2eeError("invalid_object_context")
        clear = stream.read(chunk.frame.plaintext_length)
        if len(clear) != chunk.frame.plaintext_length:
            raise E2eeError("source_changed")
        digest.update(clear)
        frame_digests.append(
            sha256(clear).digest() if index // frames_per_part + 1 in needed else None
        )
    if stream.read(1) or digest.digest() != plaintext_sha256:
        raise E2eeError("source_changed")

    for number in missing:
        first = (number - 1) * frames_per_part
        last = min(first + frames_per_part, len(plan.chunks))
        chunk = plan.chunks[first]
        stream.seek(start + chunk.plaintext_offset)
        spool.seek(chunk.ciphertext_offset)
        part_digest = sha256() if last - first > 1 else None
        part_length = 0
        for index in range(first, last):
            clear = stream.read(plan.chunks[index].frame.plaintext_length)
            # Check the exact buffer before reusing this frame's nonce.
            if sha256(clear).digest() != frame_digests[index]:
                raise E2eeError("source_changed")
            ciphertext = plan._seal_verified_chunk(clear, index)
            spool.write(ciphertext)
            if part_digest is not None:
                part_digest.update(ciphertext)
            part_length += len(ciphertext)
        expected = parts[number - 1]
        checksum = (
            part_digest.digest() if part_digest is not None else chunk.frame.sha256
        )
        if part_length != expected.ciphertext_size or checksum != expected.sha256:
            raise E2eeError("invalid_object_context")
    stream.seek(start)
