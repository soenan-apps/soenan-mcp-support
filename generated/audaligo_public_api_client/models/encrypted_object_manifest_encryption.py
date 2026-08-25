from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.encrypted_object_manifest_encryption_content_key_alg import EncryptedObjectManifestEncryptionContentKeyAlg
from ..models.encrypted_object_manifest_encryption_mode import EncryptedObjectManifestEncryptionMode
from ..models.encrypted_object_manifest_encryption_wrap_alg import EncryptedObjectManifestEncryptionWrapAlg

if TYPE_CHECKING:
    from ..models.wrapped_data_key import WrappedDataKey


T = TypeVar("T", bound="EncryptedObjectManifestEncryption")


@_attrs_define
class EncryptedObjectManifestEncryption:
    """
    Attributes:
        mode (EncryptedObjectManifestEncryptionMode):
        content_key_alg (EncryptedObjectManifestEncryptionContentKeyAlg):
        wrap_alg (EncryptedObjectManifestEncryptionWrapAlg):
        wrapped_data_key (WrappedDataKey):
    """

    mode: EncryptedObjectManifestEncryptionMode
    content_key_alg: EncryptedObjectManifestEncryptionContentKeyAlg
    wrap_alg: EncryptedObjectManifestEncryptionWrapAlg
    wrapped_data_key: WrappedDataKey

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        content_key_alg = self.content_key_alg.value

        wrap_alg = self.wrap_alg.value

        wrapped_data_key = self.wrapped_data_key.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
                "content_key_alg": content_key_alg,
                "wrap_alg": wrap_alg,
                "wrapped_data_key": wrapped_data_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.wrapped_data_key import WrappedDataKey

        d = dict(src_dict)
        mode = EncryptedObjectManifestEncryptionMode(d.pop("mode"))

        content_key_alg = EncryptedObjectManifestEncryptionContentKeyAlg(d.pop("content_key_alg"))

        wrap_alg = EncryptedObjectManifestEncryptionWrapAlg(d.pop("wrap_alg"))

        wrapped_data_key = WrappedDataKey.from_dict(d.pop("wrapped_data_key"))

        encrypted_object_manifest_encryption = cls(
            mode=mode,
            content_key_alg=content_key_alg,
            wrap_alg=wrap_alg,
            wrapped_data_key=wrapped_data_key,
        )

        return encrypted_object_manifest_encryption
