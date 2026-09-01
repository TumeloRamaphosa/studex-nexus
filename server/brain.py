"""Institutional Brain — writes agent output into the real Obsidian vault."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .config import get

DEFAULT_VAULT = Path.home() / "Obsidian" / "SecondBrain"
REPORTS_SUBDIR = "Agent Reports"


class BrainUnavailable(RuntimeError):
    """Raised when the Obsidian vault cannot be written to."""


def vault_path() -> Path:
    configured = get("OBSIDIAN_VAULT_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_VAULT


def reports_dir() -> Path:
    return vault_path() / REPORTS_SUBDIR


def _slugify(text: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    return slug[:max_len] or "note"


def write_report(role: str, question: str, answer: str) -> Path:
    """Write a timestamped markdown note into Agent Reports. Raises
    BrainUnavailable if the vault doesn't exist — never fabricates success."""
    vault = vault_path()
    if not vault.exists():
        raise BrainUnavailable(f"Obsidian vault not found at {vault}")

    target_dir = reports_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y-%m-%d_%H%M%S')}_{_slugify(role)}_{_slugify(question)}.md"
    file_path = target_dir / filename

    content = (
        f"---\n"
        f"role: {role}\n"
        f"created: {now.isoformat()}\n"
        f"source: studex-nexus/ask-brain\n"
        f"---\n\n"
        f"# {role} — {question}\n\n"
        f"{answer}\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path
