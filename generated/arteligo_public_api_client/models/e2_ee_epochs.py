from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_epoch_link import E2EeEpochLink


T = TypeVar("T", bound="E2EeEpochs")


@_attrs_define
class E2EeEpochs:
    """
    Attributes:
        epochs (list[E2EeEpochLink]):
    """

    epochs: list[E2EeEpochLink]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        epochs = []
        for epochs_item_data in self.epochs:
            epochs_item = epochs_item_data.to_dict()
            epochs.append(epochs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "epochs": epochs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_epoch_link import E2EeEpochLink

        d = dict(src_dict)
        epochs = []
        _epochs = d.pop("epochs")
        for epochs_item_data in _epochs:
            epochs_item = E2EeEpochLink.from_dict(epochs_item_data)

            epochs.append(epochs_item)

        e2_ee_epochs = cls(
            epochs=epochs,
        )

        e2_ee_epochs.additional_properties = d
        return e2_ee_epochs

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
