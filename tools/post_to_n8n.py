"""Generic n8n webhook POST helper. Schema-agnostic.

The routine assembles + validates its own payload, then hands it here.
This module knows nothing about specific payload shapes.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests


def post_payload(
    payload: dict[str, Any],
    *,
    webhook_url: str,
    source_header: str = "claude-code-routine",
    timeout: int = 60,
    retries: int = 1,
    retry_sleep_seconds: int = 60,
    archive_path: Path | None = None,
) -> dict[str, Any]:
    """POST a JSON payload to an n8n webhook.

    Args:
        payload: dict to send (already assembled + schema-validated by caller).
        webhook_url: full URL of the n8n webhook.
        source_header: value for the X-Source header (default 'claude-code-routine').
        timeout: per-request timeout in seconds.
        retries: number of retries after the first failure.
        retry_sleep_seconds: pause between attempts.
        archive_path: if provided, the payload is written there before POSTing.

    Returns:
        {
            "status":   "ok" | "error",
            "http_code": int,
            "response":  dict | str,    # parsed JSON if possible, else text
            "attempts":  int,
        }
    """
    if archive_path is not None:
        archive_path = Path(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    attempt = 0
    last_err: str | None = None
    headers = {"X-Source": source_header, "Content-Type": "application/json"}

    while attempt <= retries:
        attempt += 1
        try:
            r = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            if 200 <= r.status_code < 300:
                try:
                    body: dict | str = r.json()
                except ValueError:
                    body = r.text
                return {
                    "status": "ok",
                    "http_code": r.status_code,
                    "response": body,
                    "attempts": attempt,
                }
            last_err = f"HTTP {r.status_code}: {r.text[:500]}"
        except requests.RequestException as e:
            last_err = str(e)

        if attempt <= retries:
            time.sleep(retry_sleep_seconds)

    return {
        "status": "error",
        "http_code": 0,
        "response": last_err or "unknown error",
        "attempts": attempt,
    }
