"""Live credential status — booleans and evidence only. Never return secret values."""

from __future__ import annotations

import os
import shutil
import subprocess


def _env(*names: str) -> bool:
    return any(bool(os.environ.get(name, "").strip()) for name in names)


def _gh_auth() -> tuple[bool, str]:
    gh = shutil.which("gh")
    if not gh:
        return False, "gh CLI missing"
    try:
        result = subprocess.run(
            [gh, "auth", "status"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        out = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and "Logged in to github.com" in out:
            return True, "gh auth keyring session"
        return False, "gh auth not logged in"
    except Exception as exc:  # noqa: BLE001
        return False, type(exc).__name__


def status() -> list[dict]:
    github_ok, github_evidence = _gh_auth()
    rows = [
        {
            "id": "queen",
            "name": "Queen (OpenRouter)",
            "active": _env("OPENROUTER_API_KEY", "OPENAI_COMPAT_API_KEY"),
            "evidence": "OPENROUTER_API_KEY present" if _env("OPENROUTER_API_KEY") else "key missing",
        },
        {
            "id": "croc",
            "name": "Croc (Orgo)",
            "active": _env("ORGO_API_KEY"),
            "evidence": "ORGO_API_KEY present" if _env("ORGO_API_KEY") else "key missing",
        },
        {
            "id": "cashclaw",
            "name": "CashClaw (Stripe)",
            "active": _env("STRIPE_SECRET_KEY", "STRIPE_API_KEY", "CASHCLAW_STRIPE_KEY"),
            "evidence": "Stripe env present" if _env("STRIPE_SECRET_KEY", "STRIPE_API_KEY", "CASHCLAW_STRIPE_KEY") else "Stripe env not in this process — Robusca reports connected elsewhere",
        },
        {
            "id": "whatsapp",
            "name": "WhatsApp (Base44 / Meta)",
            "active": _env("WHATSAPP_TOKEN", "META_WHATSAPP_TOKEN", "BASE44_API_KEY"),
            "evidence": "WhatsApp env present" if _env("WHATSAPP_TOKEN", "META_WHATSAPP_TOKEN", "BASE44_API_KEY") else "token not in this process — Robusca reports +1 703-457-1882 active",
        },
        {
            "id": "github",
            "name": "GitHub PAT",
            "active": github_ok or _env("GITHUB_TOKEN", "GH_TOKEN"),
            "evidence": github_evidence,
        },
    ]
    for row in rows:
        row["status"] = "active" if row["active"] else "unknown"
    return rows
