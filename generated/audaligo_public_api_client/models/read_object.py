from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.read_object_canonicalization import ReadObjectCanonicalization
from ..models.read_object_content_key_alg import ReadObjectContentKeyAlg
from ..models.read_object_manifest_type import ReadObjectManifestType
from ..models.read_object_security_scope import ReadObjectSecurityScope
from ..models.read_object_suite_id import ReadObjectSuiteId
from ..models.read_object_wrap_alg import ReadObjectWrapAlg

if TYPE_CHECKING:
    from ..models.descriptor_chunk import DescriptorChunk


T = TypeVar("T", bound="ReadObject")


@_attrs_define
class ReadObject:
    """
    Attributes:
        manifest_version (int):
        manifest_type (ReadObjectManifestType):
        canonicalization (ReadObjectCanonicalization):
        suite_id (ReadObjectSuiteId):
        security_scope (ReadObjectSecurityScope):
        content_key_alg (ReadObjectContentKeyAlg):
        wrap_alg (ReadObjectWrapAlg):
        project_id (str):
        share_id (str):
        file_id (str):
        epoch (int):
        object_id (str):
        plaintext_size (int):
        ciphertext_size (int):
        chunk_size (int):
        chunk_count (int):
        nonce_base_b64_u (str):
        storage_mode (str):
        chunks (list[DescriptorChunk]):
    """

    manifest_version: int
    manifest_type: ReadObjectManifestType
    canonicalization: ReadObjectCanonicalization
    suite_id: ReadObjectSuiteId
    security_scope: ReadObjectSecurityScope
    content_key_alg: ReadObjectContentKeyAlg
    wrap_alg: ReadObjectWrapAlg
    project_id: str
    share_id: str
    file_id: str
    epoch: int
    object_id: str
    plaintext_size: int
    ciphertext_size: int
    chunk_size: int
    chunk_count: int
    nonce_base_b64_u: str
    storage_mode: str
    chunks: list[DescriptorChunk]

    def to_dict(self) -> dict[str, Any]:
        manifest_version = self.manifest_version

        manifest_type = self.manifest_type.value

        canonicalization = self.canonicalization.value

        suite_id = self.suite_id.value

        security_scope = self.security_scope.value

        content_key_alg = self.content_key_alg.value

        wrap_alg = self.wrap_alg.value

        project_id = self.project_id

        share_id = self.share_id

        file_id = self.file_id

        epoch = self.epoch

        object_id = self.object_id

        plaintext_size = self.plaintext_size

        ciphertext_size = self.ciphertext_size

        chunk_size = self.chunk_size

        chunk_count = self.chunk_count

        nonce_base_b64_u = self.nonce_base_b64_u

        storage_mode = self.storage_mode

        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "manifestVersion": manifest_version,
                "manifestType": manifest_type,
                "canonicalization": canonicalization,
                "suiteId": suite_id,
                "securityScope": security_scope,
                "contentKeyAlg": content_key_alg,
                "wrapAlg": wrap_alg,
                "projectId": project_id,
                "shareId": share_id,
                "fileId": file_id,
                "epoch": epoch,
                "objectId": object_id,
                "plaintextSize": plaintext_size,
                "ciphertextSize": ciphertext_size,
                "chunkSize": chunk_size,
                "chunkCount": chunk_count,
                "nonceBaseB64u": nonce_base_b64_u,
                "storageMode": storage_mode,
                "chunks": chunks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.descriptor_chunk import DescriptorChunk

        d = dict(src_dict)
        manifest_version = d.pop("manifestVersion")

        manifest_type = ReadObjectManifestType(d.pop("manifestType"))

        canonicalization = ReadObjectCanonicalization(d.pop("canonicalization"))

        suite_id = ReadObjectSuiteId(d.pop("suiteId"))

        security_scope = ReadObjectSecurityScope(d.pop("securityScope"))

        content_key_alg = ReadObjectContentKeyAlg(d.pop("contentKeyAlg"))

        wrap_alg = ReadObjectWrapAlg(d.pop("wrapAlg"))

        project_id = d.pop("projectId")

        share_id = d.pop("shareId")

        file_id = d.pop("fileId")

        epoch = d.pop("epoch")

        object_id = d.pop("objectId")

        plaintext_size = d.pop("plaintextSize")

        ciphertext_size = d.pop("ciphertextSize")

        chunk_size = d.pop("chunkSize")

        chunk_count = d.pop("chunkCount")

        nonce_base_b64_u = d.pop("nonceBaseB64u")

        storage_mode = d.pop("storageMode")

        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = DescriptorChunk.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        read_object = cls(
            manifest_version=manifest_version,
            manifest_type=manifest_type,
            canonicalization=canonicalization,
            suite_id=suite_id,
            security_scope=security_scope,
            content_key_alg=content_key_alg,
            wrap_alg=wrap_alg,
            project_id=project_id,
            share_id=share_id,
            file_id=file_id,
            epoch=epoch,
            object_id=object_id,
            plaintext_size=plaintext_size,
            ciphertext_size=ciphertext_size,
            chunk_size=chunk_size,
            chunk_count=chunk_count,
            nonce_base_b64_u=nonce_base_b64_u,
            storage_mode=storage_mode,
            chunks=chunks,
        )

        return read_object
