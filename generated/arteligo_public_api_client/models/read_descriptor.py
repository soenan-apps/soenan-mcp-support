from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

from ..models.read_descriptor_contract import ReadDescriptorContract

if TYPE_CHECKING:
    from ..models.read_object import ReadObject
    from ..models.read_project_file import ReadProjectFile
    from ..models.wrapped_data_key import WrappedDataKey


T = TypeVar("T", bound="ReadDescriptor")


@_attrs_define
class ReadDescriptor:
    """
    Attributes:
        v (int):
        contract (ReadDescriptorContract):
        wrapped_data_key (WrappedDataKey):
        project_file (ReadProjectFile):
        object_ (ReadObject):
    """

    v: int
    contract: ReadDescriptorContract
    wrapped_data_key: WrappedDataKey
    project_file: ReadProjectFile
    object_: ReadObject

    def to_dict(self) -> dict[str, Any]:
        v = self.v

        contract = self.contract.value

        wrapped_data_key = self.wrapped_data_key.to_dict()

        project_file = self.project_file.to_dict()

        object_ = self.object_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "v": v,
                "contract": contract,
                "wrappedDataKey": wrapped_data_key,
                "projectFile": project_file,
                "object": object_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.read_object import ReadObject
        from ..models.read_project_file import ReadProjectFile
        from ..models.wrapped_data_key import WrappedDataKey

        d = dict(src_dict)
        v = d.pop("v")

        contract = ReadDescriptorContract(d.pop("contract"))

        wrapped_data_key = WrappedDataKey.from_dict(d.pop("wrappedDataKey"))

        project_file = ReadProjectFile.from_dict(d.pop("projectFile"))

        object_ = ReadObject.from_dict(d.pop("object"))

        read_descriptor = cls(
            v=v,
            contract=contract,
            wrapped_data_key=wrapped_data_key,
            project_file=project_file,
            object_=object_,
        )

        return read_descriptor
