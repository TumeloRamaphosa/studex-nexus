# Studex Nexus — Architecture Notes

Captured from conversation on 2026-08-21. This is the working spec for how
`studex-nexus` (this repo) fits into the larger Studex/STUDX system. Treat
this as living documentation — update it as decisions change.

## System of record map

Each tool has one clear job. Nexus's dashboard reflects state from these
systems; it does not replace them.

| System | Role |
|---|---|
| **Huly** | System of record (issues, projects, tasks) |
| **OpenMausBot** | Direct human ↔ agent interaction |
| **Buzz** | Agent/human office (chat/presence) |
| **Discord** | Communities, gaming, external groups |
| **Obsidian** | Institutional brain (notes, knowledge, memory) |
| **GitHub / Gitea** | Code state |
| **STUDX OS** | Glue — orchestration layer tying the above together |
| **Notion** | Kanban / content calendar (used by Nexus for content ops) |

## High-level topology

```
STUDX Workspace
      │
      ├── Buzz
      ├── Discord
      ├── Huly / ClickUp
      ├── Notion / Drive
      ├── Obsidian Brain
      │
      └── Agent Control Plane
              │
              ├── Codex
              ├── MiniMax
              ├── Hermes
              ├── OpenMausBot
              └── Base44 agents
                     │
                     ↓
                 VM Fleet
                     │
             ┌───────┼────────┐
             ↓       ↓        ↓
          Rwanda   Content   Research
            VM       VM        VM
                     │
                 Gitea/GitHub

VM 1 — OPERATIONS: Huly, Postgres, event bus, STUDX API, Vault/Gatekeeper
VM 2 — BRAIN: Obsidian sync, knowledge graph, vector DB, Tencent Agent Memory
VM 3 — AGENT FACTORY: Hermes, DeerFlow, AutoResearch, MiroFish, Agency Agents, Gauntlet

Laptop: OpenMausBot, Codex, Claude, MiniMax, Ollama/MLX, STUDX CLI
```

This is **infrastructure-scale** and is treated as a later phase — Nexus does
not fake or mock this; if/when these VMs exist, Nexus should read real status
from them (health checks, not decoration).

## Event taxonomy (for the event bus on VM 1 — Operations)

Planned event types other agents/VMs should be able to emit:

```
meeting.created
meeting.completed
issue.created
issue.closed
research.completed
simulation.completed
proposal.sent
partner.updated
agent.started
agent.failed
vm.offline
vm.recovered
secret.requested
approval.required
task.completed
```

Example payload shape:
```json
{
  "type": "task.completed",
  "project": "rwanda",
  "actor": "agent:coffee-research-03",
  "source": "openmausbot",
  "timestamp": "...",
  "payload": {}
}
```

Nexus should eventually expose a simple `/api/events` endpoint (POST to
ingest, GET to list recent) as a lightweight in-process version of this bus,
before a dedicated event-bus service exists on VM 1.

## Daily Briefing panel (UI concept, not yet implemented)

A "good morning" summary view was sketched with these sections:
- **Today** — calendar/schedule for the day
- **Missions** — named projects (Rwanda, Nigeria, Russia, Cape Town) with
  progress bars
- **Agents** — counts: online / working / waiting / blocked
- **VMs** — health fraction (e.g. 7/8 healthy)
- **Research** — active running experiments/studies by tool (MiroFish,
  AutoResearch, Investment studies)
- **Priority** — flagged action items needing attention

This has no live data source yet. Candidate sources per section:
- Today → Google Calendar or Notion calendar DB
- Missions → Notion database (status/progress property) or Huly projects
- Agents/VMs → the event bus / health-check endpoints once VM fleet exists
- Research → whatever tracks MiroFish/AutoResearch runs (TBD, not yet
  identified)

**Status: deferred.** Do not fake these numbers with `Math.random()` —
if we build this panel, it starts empty/"no data" until a real source is
wired in, per the standing rule that dashboards must not show fabricated
data.

## Current implementation status (studex-nexus repo)

Backend: Python, stdlib-only HTTP server (`server/app.py`), no framework
dependency. Frontend: static HTML/CSS/JS in `public/`.

| Connector | Status as of 2026-08-21 |
|---|---|
| Ollama Cloud | ✅ Connected (19 models) |
| Blotato | ✅ Connected (6 accounts) |
| Higgsfield (CLI) | ✅ Connected (max plan) |
| FeedHive | ❌ Key valid, Business trial not activated — skipped for now |
| Freepik | ❌ Key rejected/invalid by their API — skipped for now |
| Orgo | ⚠️ Key present, no status() check implemented — skipped for now |
| Notion | ⚠️ Blocked — needs integration token + shared database URL |

Known gap: `/api/status` returns connector health but the frontend
(`public/index.html` + `app.js`) never renders it. Fixing this is part of
"finish building, all connected all working."
