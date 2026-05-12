"""Test the generic tools.post_to_n8n helper. No network — mocks only."""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.post_to_n8n import post_payload


def _mock_response(status_code: int, body: dict | str):
    m = MagicMock()
    m.status_code = status_code
    if isinstance(body, dict):
        m.json.return_value = body
        m.text = json.dumps(body)
    else:
        m.json.side_effect = ValueError
        m.text = body
    return m


def test_post_success_returns_ok(tmp_path):
    archive = tmp_path / "archive" / "test.json"
    with patch("tools.post_to_n8n.requests.post") as p:
        p.return_value = _mock_response(200, {"id": "abc"})
        result = post_payload(
            {"hello": "world"},
            webhook_url="https://example/webhook",
            archive_path=archive,
        )
    assert result["status"] == "ok"
    assert result["http_code"] == 200
    assert result["attempts"] == 1
    assert result["response"] == {"id": "abc"}
    assert archive.exists()
    assert json.loads(archive.read_text())["hello"] == "world"


def test_post_retries_on_failure():
    with patch("tools.post_to_n8n.requests.post") as p, \
         patch("tools.post_to_n8n.time.sleep"):
        p.side_effect = [
            _mock_response(500, "server boom"),
            _mock_response(200, {"id": "ok"}),
        ]
        result = post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            retries=1,
        )
    assert result["status"] == "ok"
    assert result["http_code"] == 200
    assert result["attempts"] == 2


def test_post_gives_up_after_retries():
    with patch("tools.post_to_n8n.requests.post") as p, \
         patch("tools.post_to_n8n.time.sleep"):
        p.return_value = _mock_response(500, "still bad")
        result = post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            retries=2,
        )
    assert result["status"] == "error"
    assert result["attempts"] == 3
    assert "HTTP 500" in result["response"]


def test_post_sends_correct_headers():
    with patch("tools.post_to_n8n.requests.post") as p:
        p.return_value = _mock_response(200, {"ok": True})
        post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            source_header="claude-code-routine",
        )
    call_kwargs = p.call_args.kwargs
    assert call_kwargs["headers"]["X-Source"] == "claude-code-routine"
    assert call_kwargs["headers"]["Content-Type"] == "application/json"
    assert call_kwargs["json"] == {"x": 1}
