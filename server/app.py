#!/usr/bin/env python3
"""STUDEX NEXUS Content Engine — API server."""

from __future__ import annotations

import json
import mimetypes
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from server.config import ROOT, get, load_env
from server.connectors import blotato, feedhive, freepik, ollama
from server import brain, store

PUBLIC_DIR = ROOT / "public"


def _port() -> int:
    return int(get("PORT", "5050"))


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    return json.loads(handler.rfile.read(length).decode())


def _higgsfield_status() -> dict:
    try:
        result = subprocess.run(
            ["higgsfield", "account", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"connected": True, "detail": result.stdout.strip()}
        return {"connected": False, "error": result.stderr.strip() or "Not authenticated"}
    except FileNotFoundError:
        return {
            "connected": False,
            "error": "CLI not installed — run: curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh",
        }
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": str(exc)}


class NexusHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: ARG002
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            return _json_response(
                self,
                200,
                {
                    "systemStatus": "ACTIVE",
                    "lastRun": datetime.now(timezone.utc).strftime("Today %H:%M"),
                    "connectors": {
                        "ollama": ollama.status(),
                        "blotato": blotato.status(),
                        "feedhive": feedhive.status(),
                        "freepik": freepik.status(),
                        "higgsfield": _higgsfield_status(),
                    },
                    "workflows": [
                        {"name": "Daily Content Gen", "schedule": "Daily at 07:00", "status": "green"},
                        {"name": "Auto-Meat Engine", "schedule": "Every 6 hours", "status": "green"},
                        {"name": "Approval Gate", "schedule": "On-demand", "status": "green"},
                        {"name": "Posting Pipeline", "schedule": "Blotato queue", "status": "green"},
                        {"name": "Influencer Sync", "schedule": "Every 4 hours", "status": "amber"},
                        {"name": "Analytics Collector", "schedule": "Every 15 min", "status": "green"},
                    ],
                },
            )

        if path == "/api/accounts":
            try:
                return _json_response(self, 200, blotato.list_accounts())
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        if path == "/api/dashboard":
            try:
                raw = blotato.list_posts(limit=50)
                posts = blotato.normalize_posts(raw)
                partitioned = blotato.partition_posts(posts)
                pending = store.list_pending()
                recs = [r for r in store.list_recommendations() if r.get("status") == "pending"]
                return _json_response(
                    self,
                    200,
                    {
                        "scheduled": partitioned["scheduled"],
                        "postedToday": partitioned["postedToday"],
                        "pending": pending,
                        "recommendations": recs,
                        "counts": {
                            "scheduled": len(partitioned["scheduled"]),
                            "pending": len(pending),
                            "postedToday": len(partitioned["postedToday"]),
                            "recommendations": len(recs),
                        },
                    },
                )
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        if path == "/api/recommendations":
            return _json_response(self, 200, {"items": store.list_recommendations()})

        if path.startswith("/api/freepik/search"):
            query = parsed.query.replace("q=", "").replace("+", " ") or "premium beef"
            try:
                return _json_response(self, 200, freepik.search_resources(query))
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        return self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        body = _read_json(self)

        if path == "/api/generate/recommendations":
            try:
                count = int(body.get("count", 3))
                items = ollama.generate_recommendations(count)
                saved = store.upsert_recommendations(items)
                return _json_response(self, 200, {"items": saved})
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        if path == "/api/generate/post":
            try:
                platform = body.get("platform", "Instagram")
                topic = body.get("topic", "Studex Meat premium beef")
                post = ollama.generate_post(platform, topic)
                entry = store.add_pending({**post, "platform": platform})
                return _json_response(self, 200, {"post": entry})
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        if path.startswith("/api/recommendations/") and path.endswith("/action"):
            rec_id = path.split("/")[3]
            action = body.get("action", "reject")
            if store.act_on_recommendation(rec_id, action):
                return _json_response(self, 200, {"ok": True})
            return _json_response(self, 404, {"error": "Not found"})

        if path == "/api/publish":
            try:
                account_id = body["accountId"]
                text = body["text"]
                platform = body.get("platform", "instagram").lower()
                media = body.get("mediaUrls", [])
                scheduled = body.get("scheduledTime")
                result = blotato.publish_post(account_id, text, platform, media, scheduled)
                post_id = body.get("pendingId")
                if post_id:
                    store.remove_pending(post_id)
                return _json_response(self, 200, result)
            except KeyError as exc:
                return _json_response(self, 400, {"error": f"Missing field: {exc.args[0]}"})
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": str(exc)})

        if path == "/api/brain/ask":
            role = (body.get("role") or "").strip()
            question = (body.get("question") or "").strip()
            if not role or not question:
                return _json_response(self, 400, {"error": "role and question are required"})
            try:
                answer = ollama.ask_as_role(role, question)
            except Exception as exc:  # noqa: BLE001
                return _json_response(self, 502, {"error": f"Model call failed: {exc}"})
            try:
                note_path = brain.write_report(role, question, answer)
            except brain.BrainUnavailable as exc:
                return _json_response(self, 502, {"error": str(exc), "answer": answer})
            return _json_response(
                self,
                200,
                {"answer": answer, "notePath": str(note_path)},
            )

        if path == "/api/portal/login":
            password = body.get("password", "")
            if password == get("PORTAL_PASSWORD", "nexus2026"):
                return _json_response(self, 200, {"ok": True})
            return _json_response(self, 401, {"error": "Invalid access code"})

        return _json_response(self, 404, {"error": "Not found"})

    def _serve_static(self, path: str) -> None:
        if path in ("/", ""):
            path = "/index.html"
        file_path = (PUBLIC_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(PUBLIC_DIR.resolve())):
            self.send_error(403)
            return
        if not file_path.exists():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    load_env()
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    port = _port()
    server = ThreadingHTTPServer(("0.0.0.0", port), NexusHandler)
    print(f"STUDEX NEXUS running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
