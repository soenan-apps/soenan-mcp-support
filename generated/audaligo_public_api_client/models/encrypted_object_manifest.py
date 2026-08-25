from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.encrypted_object_manifest_suite_id import EncryptedObjectManifestSuiteId
from ..models.encrypted_object_manifest_type import EncryptedObjectManifestType

if TYPE_CHECKING:
    from ..models.encrypted_object_manifest_encryption import EncryptedObjectManifestEncryption
    from ..models.manifest_object import ManifestObject


T = TypeVar("T", bound="EncryptedObjectManifest")


@_attrs_define
class EncryptedObjectManifest:
    """
    Attributes:
        v (int):
        type_ (EncryptedObjectManifestType):
        suite_id (EncryptedObjectManifestSuiteId):
        encryption (EncryptedObjectManifestEncryption):
        object_ (ManifestObject):
    """

    v: int
    type_: EncryptedObjectManifestType
    suite_id: EncryptedObjectManifestSuiteId
    encryption: EncryptedObjectManifestEncryption
    object_: ManifestObject

    def to_dict(self) -> dict[str, Any]:
        v = self.v

        type_ = self.type_.value

        suite_id = self.suite_id.value

        encryption = self.encryption.to_dict()

        object_ = self.object_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "type": type_,
                "suite_id": suite_id,
                "encryption": encryption,
                "object": object_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.encrypted_object_manifest_encryption import EncryptedObjectManifestEncryption
        from ..models.manifest_object import ManifestObject

        d = dict(src_dict)
        v = d.pop("v")

        type_ = EncryptedObjectManifestType(d.pop("type"))

        suite_id = EncryptedObjectManifestSuiteId(d.pop("suite_id"))

        encryption = EncryptedObjectManifestEncryption.from_dict(d.pop("encryption"))

        object_ = ManifestObject.from_dict(d.pop("object"))

        encrypted_object_manifest = cls(
            v=v,
            type_=type_,
            suite_id=suite_id,
            encryption=encryption,
            object_=object_,
        )

        return encrypted_object_manifest
