from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_key_claim import FileKeyClaim
    from ..models.read_descriptor import ReadDescriptor


T = TypeVar("T", bound="ReadDescriptorResponse")


@_attrs_define
class ReadDescriptorResponse:
    """
    Attributes:
        ok (bool):
        descriptor (ReadDescriptor):
        key_claim (FileKeyClaim):
        transfer_continuation (str | Unset):
    """

    ok: bool
    descriptor: ReadDescriptor
    key_claim: FileKeyClaim
    transfer_continuation: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        ok = self.ok

        descriptor = self.descriptor.to_dict()

        key_claim = self.key_claim.to_dict()
        transfer_continuation = self.transfer_continuation

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ok": ok,
                "descriptor": descriptor,
                "keyClaim": key_claim,
            }
        )
        if transfer_continuation is not UNSET:
            field_dict["transferContinuation"] = transfer_continuation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_key_claim import FileKeyClaim
        from ..models.read_descriptor import ReadDescriptor

        d = dict(src_dict)
        ok = d.pop("ok")

        descriptor = ReadDescriptor.from_dict(d.pop("descriptor"))

        key_claim = FileKeyClaim.from_dict(d.pop("keyClaim"))
        transfer_continuation = d.pop("transferContinuation", UNSET)

        read_descriptor_response = cls(
            ok=ok,
            descriptor=descriptor,
            key_claim=key_claim,
            transfer_continuation=transfer_continuation,
        )

        return read_descriptor_response
