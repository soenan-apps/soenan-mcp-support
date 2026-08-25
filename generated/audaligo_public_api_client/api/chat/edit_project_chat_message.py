from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...models.chat_event import ChatEvent
from ...models.edit_chat_message_request import EditChatMessageRequest
from ...models.edit_project_chat_message_sec_fetch_site import EditProjectChatMessageSecFetchSite
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project: str,
    message: str,
    *,
    body: EditChatMessageRequest,
    origin: str,
    sec_fetch_site: EditProjectChatMessageSecFetchSite | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Origin"] = origin

    if not isinstance(sec_fetch_site, Unset):
        headers["Sec-Fetch-Site"] = str(sec_fetch_site)

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/projects/{project}/chat/messages/{message}".format(
            project=quote(str(project), safe=""),
            message=quote(str(message), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ChatEvent | ErrorEnvelope:
    if response.status_code == 200:
        response_200 = ChatEvent.from_dict(response.json())

        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ChatEvent | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    message: str,
    *,
    client: AuthenticatedClient | Client,
    body: EditChatMessageRequest,
    origin: str,
    sec_fetch_site: EditProjectChatMessageSecFetchSite | Unset = UNSET,
) -> Response[ChatEvent | ErrorEnvelope]:
    """
    Args:
        project (str):
        message (str):
        origin (str):
        sec_fetch_site (EditProjectChatMessageSecFetchSite | Unset):
        body (EditChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatEvent | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        message=message,
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
    message: str,
    *,
    client: AuthenticatedClient | Client,
    body: EditChatMessageRequest,
    origin: str,
    sec_fetch_site: EditProjectChatMessageSecFetchSite | Unset = UNSET,
) -> ChatEvent | ErrorEnvelope | None:
    """
    Args:
        project (str):
        message (str):
        origin (str):
        sec_fetch_site (EditProjectChatMessageSecFetchSite | Unset):
        body (EditChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatEvent | ErrorEnvelope
    """

    return sync_detailed(
        project=project,
        message=message,
        client=client,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    ).parsed


async def asyncio_detailed(
    project: str,
    message: str,
    *,
    client: AuthenticatedClient | Client,
    body: EditChatMessageRequest,
    origin: str,
    sec_fetch_site: EditProjectChatMessageSecFetchSite | Unset = UNSET,
) -> Response[ChatEvent | ErrorEnvelope]:
    """
    Args:
        project (str):
        message (str):
        origin (str):
        sec_fetch_site (EditProjectChatMessageSecFetchSite | Unset):
        body (EditChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatEvent | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        project=project,
        message=message,
        body=body,
        origin=origin,
        sec_fetch_site=sec_fetch_site,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    message: str,
    *,
    client: AuthenticatedClient | Client,
    body: EditChatMessageRequest,
    origin: str,
    sec_fetch_site: EditProjectChatMessageSecFetchSite | Unset = UNSET,
) -> ChatEvent | ErrorEnvelope | None:
    """
    Args:
        project (str):
        message (str):
        origin (str):
        sec_fetch_site (EditProjectChatMessageSecFetchSite | Unset):
        body (EditChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatEvent | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            project=project,
            message=message,
            client=client,
            body=body,
            origin=origin,
            sec_fetch_site=sec_fetch_site,
        )
    ).parsed
