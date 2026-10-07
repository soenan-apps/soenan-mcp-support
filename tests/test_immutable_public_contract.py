from types import SimpleNamespace

import httpx
import pytest

from soenan_arteligo_support.e2ee._api import GeneratedAPI
from soenan_arteligo_support.e2ee._crypto import E2eeError


def test_generated_immutable_selection_reuses_the_fixed_snapshot_cursor():
    requests = []

    def send(request):
        requests.append(request)
        return httpx.Response(200, json={
            "records": [], "commands": {}, "cursor": 5,
            "snapshot_cursor": 9, "has_more": False, "server_time": 1791356400,
        })

    oauth = SimpleNamespace(arteligo_origin="https://arteligo.test", access_token=lambda: "fixture-token")
    api = GeneratedAPI(oauth, transport=httpx.MockTransport(send))
    page = api.call("e2eeGetImmutable", scope_id="prj_test", kind="chat", after=5, snapshot_cursor=9, limit=2)
    assert page["cursor"] == 5
    assert page["snapshot_cursor"] == 9
    assert page["records"] == []
    assert requests[0].url.path == "/api/e2ee/scopes/prj_test/immutable"
    assert dict(requests[0].url.params) == {"kind": "chat", "after": "5", "snapshot_cursor": "9", "limit": "2"}


def test_generated_client_preserves_the_conversation_format_update_error():
    oauth = SimpleNamespace(arteligo_origin="https://arteligo.test", access_token=lambda: "fixture-token")
    api = GeneratedAPI(oauth, transport=httpx.MockTransport(lambda _request: httpx.Response(409, json={
        "error": {"code": "content_format_update_required", "message": "update required"},
    })))
    with pytest.raises(E2eeError, match="content_format_update_required"):
        api.call("e2eeGetImmutable", scope_id="prj_test", kind="chat")
