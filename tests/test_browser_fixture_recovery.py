import importlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_e2ee import MemoryAPI, new_session

from soenan_arteligo_support.e2ee import E2eeCrypto, E2eeError


@pytest.fixture
def fixture_tool(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "tool"))
    return importlib.import_module("browser_metadata_fixture")


def test_committed_creation_with_lost_response_keeps_recoverable_public_intent(
    fixture_tool, monkeypatch, tmp_path
):
    api = MemoryAPI(E2eeCrypto())
    session, _, _ = new_session(api, setup=True)
    call = api.call
    path = tmp_path / "fixture.json"

    def lose_response(operation, **arguments):
        result = call(operation, **arguments)
        if operation == "e2eeCreateProject":
            intent = json.loads(path.read_text())
            assert intent["state"] == "creating"
            assert intent["scope_id"] in api.projects
            raise E2eeError("connection_lost")
        return result

    monkeypatch.setattr(api, "call", lose_response)
    with pytest.raises(E2eeError, match="connection_lost"):
        fixture_tool.create_fixture_project(
            session, "org-test", path, "https://test.local.soenan.dev", 1, "Fixture"
        )
    intent = json.loads(path.read_text())
    assert "project_create_command_id" not in intent
    monkeypatch.setattr(api, "call", call)
    project = fixture_tool.recover_creation_proof(session, intent)
    assert project["value"]["title"] == intent["title"]
    assert intent["project_create_command_id"]
    intent["project_create_command_id"] = "wrong-proof"
    with pytest.raises(E2eeError, match="fixture_creation_proof_invalid"):
        fixture_tool.recover_creation_proof(session, intent)
    session.lock()


def test_bridge_deadline_terminates_unresponsive_child(fixture_tool, monkeypatch):
    bridge_module = importlib.import_module("_browser_fixture_session")
    original = subprocess.Popen
    monkeypatch.setattr(
        bridge_module.subprocess,
        "Popen",
        lambda *args, **kwargs: original(
            [sys.executable, "-c", "import sys; sys.stdin.buffer.read()"], **kwargs
        ),
    )
    bridge = bridge_module.BrowserBridge(
        SimpleNamespace(node="unused", cdp_url="unused", origin="https://local.test")
    )
    monkeypatch.setattr(bridge_module.select, "select", lambda *args: ([], [], []))
    try:
        with pytest.raises(E2eeError, match="browser_request_timeout"):
            bridge.call({"action": "request"})
        assert bridge.process.poll() is not None
    finally:
        bridge.stop()
