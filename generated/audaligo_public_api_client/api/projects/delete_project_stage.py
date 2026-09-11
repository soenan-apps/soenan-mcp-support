from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.delete_project_stage_sec_fetch_site import DeleteProjectStageSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    stage: str,
    *,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectStageSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    params: dict[str, Any] = {}

    params["expectedRevision"] = expected_revision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/projects/{project}/stages/{stage}".format(
            project=quote(str(project), safe=""),
            stage=quote(str(stage), safe=""),
        ),
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorEnvelope:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectStageSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        project (str):
        stage (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectStageSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
        expected_revision=expected_revision,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectStageSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        project (str):
        stage (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectStageSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        stage=stage,
        client=client,
        expected_revision=expected_revision,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectStageSecFetchSite | Unset = UNSET,
) -> Response[Any | ErrorEnvelope]:
    """
    Args:
        project (str):
        stage (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectStageSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        stage=stage,
        expected_revision=expected_revision,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    stage: str,
    *,
    client: AuthenticatedClient,
    expected_revision: int,
    origin: str,
    sec_fetch_site: DeleteProjectStageSecFetchSite | Unset = UNSET,
) -> Any | ErrorEnvelope | None:
    """
    Args:
        project (str):
        stage (str):
        expected_revision (int):
        origin (str):
        sec_fetch_site (DeleteProjectStageSecFetchSite | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            stage=stage,
            client=client,
            expected_revision=expected_revision,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
