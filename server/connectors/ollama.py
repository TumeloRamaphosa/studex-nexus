"""Ollama Cloud API connector."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ..config import get

BRAND_SYSTEM = """You are the Studex Meat content strategist for STUDEX NEXUS.
Brand: premium South African halaal-certified beef. Voice: confident, heritage, execution.
Tagline: Where Heritage Meets Execution.
Always respond with valid JSON only — no markdown fences."""


def _base_url() -> str:
    return get("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get('OLLAMA_API_KEY')}",
        "Content-Type": "application/json",
    }


def status() -> dict[str, Any]:
    key = get("OLLAMA_API_KEY")
    if not key:
        return {"connected": False, "error": "OLLAMA_API_KEY not set"}
    try:
        req = urllib.request.Request(
            f"{_base_url()}/api/tags",
            headers=_headers(),
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return {"connected": True, "models": len(data.get("models", []))}
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": str(exc)}


def chat(prompt: str, system: str | None = None) -> str:
    model = get("OLLAMA_MODEL", "gemma3:12b")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(
        f"{_base_url()}/api/chat",
        data=body,
        headers=_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    return data["message"]["content"]


def _parse_json(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def generate_recommendations(count: int = 3) -> list[dict[str, Any]]:
    prompt = f"""Generate {count} social media post recommendations for Studex Meat.
Return JSON array with objects containing:
- topic (short uppercase label)
- caption (post copy, 1-3 sentences)
- platform (Instagram Reels | Instagram Feed | Facebook | LinkedIn | TikTok)
- timingScore (integer 70-98)
- bestWindow (e.g. "18:00 - 20:00")
"""
    return _parse_json(chat(prompt, BRAND_SYSTEM))


def generate_post(platform: str, topic: str) -> dict[str, Any]:
    prompt = f"""Write one {platform} post about: {topic}
Return JSON with keys: caption, hashtags (array of strings)"""
    return _parse_json(chat(prompt, BRAND_SYSTEM))


def ask_as_role(role: str, question: str) -> str:
    """Plain-text answer from a role-scoped system prompt (not JSON)."""
    system = (
        f"You are the {role} for Studex Group, a South African group spanning "
        f"premium halaal beef (Studex Meat), Global Markets trading, and AI "
        f"agent operations (STUDX). Answer as the {role} would: concise, "
        f"direct, no fluff, plain text (not markdown fences, not JSON)."
    )
    return chat(question, system)
