"""Freepik API connector — stock images and AI generation."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ..config import get

BASE_URL = "https://api.freepik.com/v1"


def _headers() -> dict[str, str]:
    return {
        "x-freepik-api-key": get("FREEPIK_API_KEY"),
        "Accept": "application/json",
    }


def _request(method: str, path: str, body: dict | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {**_headers(), "Content-Type": "application/json"} if body else _headers()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode()
        try:
            detail = json.loads(payload)
        except json.JSONDecodeError:
            detail = {"message": payload}
        raise RuntimeError(f"Freepik {exc.code}: {detail}") from exc


def status() -> dict[str, Any]:
    key = get("FREEPIK_API_KEY")
    if not key:
        return {"connected": False, "error": "FREEPIK_API_KEY not set"}
    try:
        result = search_resources("premium beef food", limit=1)
        return {"connected": True, "sampleResults": len(result.get("data", []))}
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": str(exc)}


def search_resources(query: str, limit: int = 10) -> dict[str, Any]:
    from urllib.parse import quote

    return _request("GET", f"/resources?term={quote(query)}&limit={limit}")
