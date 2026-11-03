from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.authorize_o_auth_client_code_challenge_method import (
    AuthorizeOAuthClientCodeChallengeMethod,
)
from ...models.authorize_o_auth_client_prompt import AuthorizeOAuthClientPrompt
from ...models.authorize_o_auth_client_response_type import (
    AuthorizeOAuthClientResponseType,
)
from ...models.error_response import ErrorResponse
from ...models.o_auth_error_response import OAuthErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    response_type: AuthorizeOAuthClientResponseType,
    client_id: str,
    redirect_uri: str,
    resource: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: AuthorizeOAuthClientCodeChallengeMethod,
    prompt: AuthorizeOAuthClientPrompt | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_response_type = response_type.value
    params["response_type"] = json_response_type

    params["client_id"] = client_id

    params["redirect_uri"] = redirect_uri

    params["resource"] = resource

    params["scope"] = scope

    params["state"] = state

    params["code_challenge"] = code_challenge

    json_code_challenge_method = code_challenge_method.value
    params["code_challenge_method"] = json_code_challenge_method

    json_prompt: str | Unset = UNSET
    if not isinstance(prompt, Unset):
        json_prompt = prompt.value

    params["prompt"] = json_prompt

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oauth/authorize",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ErrorResponse | OAuthErrorResponse | None:
    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if response.status_code == 400:
        response_400 = OAuthErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ErrorResponse | OAuthErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    response_type: AuthorizeOAuthClientResponseType,
    client_id: str,
    redirect_uri: str,
    resource: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: AuthorizeOAuthClientCodeChallengeMethod,
    prompt: AuthorizeOAuthClientPrompt | Unset = UNSET,
) -> Response[Any | ErrorResponse | OAuthErrorResponse]:
    """Validate a first-party or MCP authorization request and enter Account sign-in or MCP consent.

    Args:
        response_type (AuthorizeOAuthClientResponseType):
        client_id (str):
        redirect_uri (str):
        resource (str):
        scope (str):
        state (str):
        code_challenge (str):
        code_challenge_method (AuthorizeOAuthClientCodeChallengeMethod):
        prompt (AuthorizeOAuthClientPrompt | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | OAuthErrorResponse]
    """

    kwargs = _get_kwargs(
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        resource=resource,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        prompt=prompt,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    response_type: AuthorizeOAuthClientResponseType,
    client_id: str,
    redirect_uri: str,
    resource: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: AuthorizeOAuthClientCodeChallengeMethod,
    prompt: AuthorizeOAuthClientPrompt | Unset = UNSET,
) -> Any | ErrorResponse | OAuthErrorResponse | None:
    """Validate a first-party or MCP authorization request and enter Account sign-in or MCP consent.

    Args:
        response_type (AuthorizeOAuthClientResponseType):
        client_id (str):
        redirect_uri (str):
        resource (str):
        scope (str):
        state (str):
        code_challenge (str):
        code_challenge_method (AuthorizeOAuthClientCodeChallengeMethod):
        prompt (AuthorizeOAuthClientPrompt | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | OAuthErrorResponse
    """

    return sync_detailed(
        client=client,
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        resource=resource,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        prompt=prompt,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    response_type: AuthorizeOAuthClientResponseType,
    client_id: str,
    redirect_uri: str,
    resource: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: AuthorizeOAuthClientCodeChallengeMethod,
    prompt: AuthorizeOAuthClientPrompt | Unset = UNSET,
) -> Response[Any | ErrorResponse | OAuthErrorResponse]:
    """Validate a first-party or MCP authorization request and enter Account sign-in or MCP consent.

    Args:
        response_type (AuthorizeOAuthClientResponseType):
        client_id (str):
        redirect_uri (str):
        resource (str):
        scope (str):
        state (str):
        code_challenge (str):
        code_challenge_method (AuthorizeOAuthClientCodeChallengeMethod):
        prompt (AuthorizeOAuthClientPrompt | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ErrorResponse | OAuthErrorResponse]
    """

    kwargs = _get_kwargs(
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        resource=resource,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        prompt=prompt,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    response_type: AuthorizeOAuthClientResponseType,
    client_id: str,
    redirect_uri: str,
    resource: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: AuthorizeOAuthClientCodeChallengeMethod,
    prompt: AuthorizeOAuthClientPrompt | Unset = UNSET,
) -> Any | ErrorResponse | OAuthErrorResponse | None:
    """Validate a first-party or MCP authorization request and enter Account sign-in or MCP consent.

    Args:
        response_type (AuthorizeOAuthClientResponseType):
        client_id (str):
        redirect_uri (str):
        resource (str):
        scope (str):
        state (str):
        code_challenge (str):
        code_challenge_method (AuthorizeOAuthClientCodeChallengeMethod):
        prompt (AuthorizeOAuthClientPrompt | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ErrorResponse | OAuthErrorResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            resource=resource,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            prompt=prompt,
        )
    ).parsed
