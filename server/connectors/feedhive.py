"""FeedHive REST API connector."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ..config import get

BASE_URL = "https://api.feedhive.com"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get('FEEDHIVE_API_KEY')}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _request(method: str, path: str, body: dict | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode()
        try:
            detail = json.loads(payload)
        except json.JSONDecodeError:
            detail = {"message": payload}
        raise RuntimeError(f"FeedHive {exc.code}: {detail}") from exc


def status() -> dict[str, Any]:
    key = get("FEEDHIVE_API_KEY")
    if not key:
        return {"connected": False, "error": "FEEDHIVE_API_KEY not set"}
    try:
        _request("GET", "/posts?limit=1")
        return {"connected": True}
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "API_ACCESS_UNAVAILABLE" in msg:
            return {
                "connected": False,
                "error": "Key valid — activate Business trial at feedhive.com to unlock API",
            }
        return {"connected": False, "error": msg}


def list_posts(limit: int = 20) -> dict[str, Any]:
    return _request("GET", f"/posts?limit={limit}")


def create_post(
    text: str,
    account_ids: list[str],
    status_value: str = "draft",
    scheduled_at: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "text": text,
        "accounts": account_ids,
        "status": status_value,
    }
    if scheduled_at:
        body["scheduled_at"] = scheduled_at
    return _request("POST", "/posts", body)
