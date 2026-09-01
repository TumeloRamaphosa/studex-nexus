"""Blotato REST API connector."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from ..config import get

BASE_URL = "https://backend.blotato.com/v2"


def _headers() -> dict[str, str]:
    return {
        "blotato-api-key": get("BLOTATO_API_KEY"),
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
        raise RuntimeError(f"Blotato {exc.code}: {detail}") from exc


def status() -> dict[str, Any]:
    key = get("BLOTATO_API_KEY")
    if not key:
        return {"connected": False, "error": "BLOTATO_API_KEY not set"}
    try:
        accounts = list_accounts()
        return {"connected": True, "accounts": len(accounts.get("items", []))}
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": str(exc)}


def list_accounts() -> dict[str, Any]:
    return _request("GET", "/users/me/accounts")


def list_posts(limit: int = 50) -> dict[str, Any]:
    return _request("GET", f"/posts?limit={limit}")


def publish_post(
    account_id: str,
    text: str,
    platform: str,
    media_urls: list[str] | None = None,
    scheduled_time: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "post": {
            "accountId": account_id,
            "content": {
                "text": text,
                "mediaUrls": media_urls or [],
                "platform": platform,
            },
            "target": {"targetType": platform},
        }
    }
    if scheduled_time:
        payload["scheduledTime"] = scheduled_time
    return _request("POST", "/posts", payload)


def normalize_posts(raw: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for post in raw.get("items", []):
        state = post.get("state", {})
        items.append(
            {
                "id": post.get("id"),
                "platform": post.get("platform", "").title(),
                "caption": post.get("text", ""),
                "mediaUrls": post.get("mediaUrls", []),
                "postTime": post.get("postTime"),
                "status": state.get("type", "unknown"),
                "postUrl": state.get("postUrl"),
            }
        )
    return items


def partition_posts(posts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    today = datetime.now(timezone.utc).date()
    scheduled: list[dict[str, Any]] = []
    posted_today: list[dict[str, Any]] = []

    for post in posts:
        status = post.get("status")
        post_time = post.get("postTime")
        if not post_time:
            continue
        dt = datetime.fromisoformat(post_time.replace("Z", "+00:00"))

        if status == "scheduled":
            scheduled.append({**post, "timeLabel": dt.strftime("%b %d, %I:%M %p")})
        elif status == "published" and dt.date() == today:
            posted_today.append({**post, "timeLabel": f"Posted {dt.strftime('%I:%M %p')}"})

    return {"scheduled": scheduled, "postedToday": posted_today}
