from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

if TYPE_CHECKING:
    from ..models.e2_ee_owner_candidate_result import E2EeOwnerCandidateResult


T = TypeVar("T", bound="E2EeGetOwnerCandidatesResponse200")


@_attrs_define
class E2EeGetOwnerCandidatesResponse200:
    """
    Attributes:
        candidates (list[E2EeOwnerCandidateResult]):
    """

    candidates: list[E2EeOwnerCandidateResult]

    def to_dict(self) -> dict[str, Any]:
        candidates = []
        for candidates_item_data in self.candidates:
            candidates_item = candidates_item_data.to_dict()
            candidates.append(candidates_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "candidates": candidates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.e2_ee_owner_candidate_result import E2EeOwnerCandidateResult

        d = dict(src_dict)
        candidates = []
        _candidates = d.pop("candidates")
        for candidates_item_data in _candidates:
            candidates_item = E2EeOwnerCandidateResult.from_dict(candidates_item_data)

            candidates.append(candidates_item)

        e2_ee_get_owner_candidates_response_200 = cls(
            candidates=candidates,
        )

        return e2_ee_get_owner_candidates_response_200
