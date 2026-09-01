"""Local JSON persistence for approval queue and recommendations."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import ROOT

DATA_DIR = ROOT / "data"
PENDING_FILE = DATA_DIR / "pending.json"
RECOMMENDATIONS_FILE = DATA_DIR / "recommendations.json"


def _read(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write(path: Path, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_pending() -> list[dict[str, Any]]:
    return _read(PENDING_FILE, [])


def add_pending(post: dict[str, Any]) -> dict[str, Any]:
    items = list_pending()
    entry = {
        "id": str(uuid.uuid4()),
        "platform": post.get("platform", "Instagram"),
        "caption": post.get("caption", ""),
        "mediaUrls": post.get("mediaUrls", []),
        "accountId": post.get("accountId"),
        "status": "pending",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _write(PENDING_FILE, items)
    return entry


def remove_pending(post_id: str) -> bool:
    items = list_pending()
    filtered = [p for p in items if p["id"] != post_id]
    if len(filtered) == len(items):
        return False
    _write(PENDING_FILE, filtered)
    return True


def list_recommendations() -> list[dict[str, Any]]:
    return _read(RECOMMENDATIONS_FILE, [])


def save_recommendations(items: list[dict[str, Any]]) -> None:
    _write(RECOMMENDATIONS_FILE, items)


def upsert_recommendations(new_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = list_recommendations()
    for item in new_items:
        existing.append(
            {
                "id": str(uuid.uuid4()),
                "topic": item.get("topic", "RECOMMENDATION"),
                "caption": item.get("caption", ""),
                "platform": item.get("platform", "Instagram"),
                "timingScore": item.get("timingScore", 80),
                "bestWindow": item.get("bestWindow", "12:00 - 14:00"),
                "status": "pending",
            }
        )
    save_recommendations(existing)
    return existing


def act_on_recommendation(rec_id: str, action: str) -> bool:
    items = list_recommendations()
    updated = []
    found = False
    for item in items:
        if item["id"] == rec_id:
            found = True
            if action == "approve":
                add_pending(
                    {
                        "platform": item.get("platform", "Instagram"),
                        "caption": item.get("caption", ""),
                    }
                )
            continue
        updated.append(item)
    if found:
        save_recommendations(updated)
    return found
