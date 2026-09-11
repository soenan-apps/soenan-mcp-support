from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.comment_envelope import CommentEnvelope
from ...models.error_envelope import ErrorEnvelope
from ...models.resolve_comment_request import ResolveCommentRequest
from ...models.resolve_timeline_comment_sec_fetch_site import (
    ResolveTimelineCommentSecFetchSite,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    comment: str,
    *,
    body: ResolveCommentRequest,
    origin: str,
    sec_fetch_site: ResolveTimelineCommentSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/comments/{comment}".format(
            project=quote(str(project), safe=""),
            comment=quote(str(comment), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CommentEnvelope | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = CommentEnvelope.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CommentEnvelope | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: ResolveCommentRequest,
    origin: str,
    sec_fetch_site: ResolveTimelineCommentSecFetchSite | Unset = UNSET,
) -> Response[CommentEnvelope | ErrorEnvelope]:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (ResolveTimelineCommentSecFetchSite | Unset):
        body (ResolveCommentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommentEnvelope | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        comment=comment,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: ResolveCommentRequest,
    origin: str,
    sec_fetch_site: ResolveTimelineCommentSecFetchSite | Unset = UNSET,
) -> CommentEnvelope | ErrorEnvelope | None:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (ResolveTimelineCommentSecFetchSite | Unset):
        body (ResolveCommentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommentEnvelope | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        comment=comment,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: ResolveCommentRequest,
    origin: str,
    sec_fetch_site: ResolveTimelineCommentSecFetchSite | Unset = UNSET,
) -> Response[CommentEnvelope | ErrorEnvelope]:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (ResolveTimelineCommentSecFetchSite | Unset):
        body (ResolveCommentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommentEnvelope | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        comment=comment,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: ResolveCommentRequest,
    origin: str,
    sec_fetch_site: ResolveTimelineCommentSecFetchSite | Unset = UNSET,
) -> CommentEnvelope | ErrorEnvelope | None:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (ResolveTimelineCommentSecFetchSite | Unset):
        body (ResolveCommentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommentEnvelope | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            comment=comment,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
