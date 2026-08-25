from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.comment_reply_request import CommentReplyRequest
from ...models.create_comment_reply_sec_fetch_site import CreateCommentReplySecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...models.reply_envelope import ReplyEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    comment: str,
    *,
    body: CommentReplyRequest,
    origin: str,
    sec_fetch_site: CreateCommentReplySecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/projects/{project}/comments/{comment}/replies".format(
            project=quote(str(project), safe=""),
            comment=quote(str(comment), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorEnvelope | ReplyEnvelope:
    if response.status_code == 201:
        response_201 = ReplyEnvelope.from_dict(response.json())

        return response_201

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ReplyEnvelope]:
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
    body: CommentReplyRequest,
    origin: str,
    sec_fetch_site: CreateCommentReplySecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ReplyEnvelope]:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (CreateCommentReplySecFetchSite | Unset):
        idempotency_key (str):
        body (CommentReplyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ReplyEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        comment=comment,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
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
    body: CommentReplyRequest,
    origin: str,
    sec_fetch_site: CreateCommentReplySecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ReplyEnvelope | None:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (CreateCommentReplySecFetchSite | Unset):
        idempotency_key (str):
        body (CommentReplyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ReplyEnvelope
    """

    return sync_detailed(
        project=project,
        comment=comment,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: CommentReplyRequest,
    origin: str,
    sec_fetch_site: CreateCommentReplySecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> Response[ErrorEnvelope | ReplyEnvelope]:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (CreateCommentReplySecFetchSite | Unset):
        idempotency_key (str):
        body (CommentReplyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ReplyEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        comment=comment,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    comment: str,
    *,
    client: AuthenticatedClient | Client,
    body: CommentReplyRequest,
    origin: str,
    sec_fetch_site: CreateCommentReplySecFetchSite | Unset = UNSET,
    idempotency_key: str,
) -> ErrorEnvelope | ReplyEnvelope | None:
    """
    Args:
        project (str):
        comment (str):
        origin (str):
        sec_fetch_site (CreateCommentReplySecFetchSite | Unset):
        idempotency_key (str):
        body (CommentReplyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ReplyEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            comment=comment,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
            idempotency_key=idempotency_key,
        )
    ).parsed
