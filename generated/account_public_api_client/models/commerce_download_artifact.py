from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommerceDownloadArtifact")


@_attrs_define
class CommerceDownloadArtifact:
    """
    Attributes:
        id (str):
        product_id (str):
        release_id (str):
        edition_id (str):
        filename (str):
        download_path (str):
        edition_name (str | Unset):
        release_name (str | Unset):
    """

    id: str
    product_id: str
    release_id: str
    edition_id: str
    filename: str
    download_path: str
    edition_name: str | Unset = UNSET
    release_name: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        product_id = self.product_id

        release_id = self.release_id

        edition_id = self.edition_id

        filename = self.filename

        download_path = self.download_path

        edition_name = self.edition_name

        release_name = self.release_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "productId": product_id,
                "releaseId": release_id,
                "editionId": edition_id,
                "filename": filename,
                "downloadPath": download_path,
            }
        )
        if edition_name is not UNSET:
            field_dict["editionName"] = edition_name
        if release_name is not UNSET:
            field_dict["releaseName"] = release_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        product_id = d.pop("productId")

        release_id = d.pop("releaseId")

        edition_id = d.pop("editionId")

        filename = d.pop("filename")

        download_path = d.pop("downloadPath")

        edition_name = d.pop("editionName", UNSET)

        release_name = d.pop("releaseName", UNSET)

        commerce_download_artifact = cls(
            id=id,
            product_id=product_id,
            release_id=release_id,
            edition_id=edition_id,
            filename=filename,
            download_path=download_path,
            edition_name=edition_name,
            release_name=release_name,
        )

        return commerce_download_artifact
