# Findings — STUDX Daily Tracker OS v0.1

Research recorded before implementation, per the planning gate. Scope is
deliberately narrowed to what can be verified today on this Mac — the wider
STUDX Alpha / multi-VM research institution vision (Buzz, MiroFish,
AutoResearch, Agency Agents, model router, investment committee, etc.) is
recorded as future direction, not built now. Building infrastructure that
can't be verified violates the "no fabricated dashboards" rule already in
`ARCHITECTURE.md`.

## What already exists and is verified working

- **`studex-nexus`** (this repo): Python stdlib HTTP server on `:5050`,
  static JS/HTML frontend. Live connectors confirmed by direct API call on
  2026-08-21: Ollama Cloud (19 models), Blotato (6 accounts), Higgsfield CLI
  (max plan). Confirmed dead: FeedHive (trial inactive), Freepik (invalid
  key). Not yet implemented: Orgo status check, Notion connector (blocked on
  credentials).
- **Obsidian "Brain"**: real vault at `/Users/tumeloramaphosa/Obsidian/SecondBrain`,
  containing `RALF/`, `RALF Loop/`, `Agent Reports/`, `Agents/`, `Daily/`,
  `Daily Logs/`, `Projects/`, `Research/`. This is the actual institutional
  memory referenced throughout prior conversation (not a mock).
- **Local models**: Ollama Cloud already wired (see `server/connectors/ollama.py`).
  LM Studio / local Ollama on this Mac + the Windows GPU box are described in
  `~/CLAUDE.md` but have no verified connector in this repo yet.

## Four-VM topology (target architecture, not yet provisioned)

Per the architecture dump, the target is 3-4 VMs:

| VM | Role |
|---|---|
| VM 1 — Operations | Huly, Postgres, event bus, STUDX API, Vault/Gatekeeper |
| VM 2 — Brain | Obsidian sync, knowledge graph, vector DB, Tencent Agent Memory |
| VM 3 — Agent Factory | Hermes, DeerFlow, AutoResearch, MiroFish, Agency Agents, Gauntlet |
| (implied VM 4) — Global Markets | Sergio/Polly workspaces: Rwanda, coffee trade, customs/trade research |

**Status: none of these VMs exist yet.** No Daytona/cloud VM has been
provisioned in this session (earlier attempt stalled on Daytona login).
v0.1 runs entirely on the local Mac. VM provisioning is future work and
must not be simulated in the dashboard.

## MCP layer

Referenced tools: `studx mcp list`, `studx mcp connect`. No MCP server for
STUDX-specific tools exists yet. Available MCP servers in this environment
(from tool list): kapture, obsidian-vault, puppeteer, composio, headroom,
cursor, playwright. The `obsidian-vault` MCP server is directly relevant to
the Brain layer and should be evaluated before hand-rolling file I/O against
the vault, if it can read/write the SecondBrain vault.

## Model layer

Target: a "STUDX Model Gateway" abstracting Grok/Kimi/MiniMax/Qwen/OpenAI/
Hermes/local models behind one interface (`studx ask --role ... --task ...`).
**Not built.** v0.1 uses the one real model connector already in this repo:
Ollama Cloud (`server/connectors/ollama.py`, `chat()` function). Adding
further providers is future work, added one at a time as each is verified
live (same standard applied to Notion/Orgo above).

## Security boundaries

- Secrets live in `.env` (gitignored), loaded via `server/config.py`.
  Never logged, never printed in full by tooling (verified pattern used
  earlier in session: length/prefix checks only, not full key dumps).
- `PORTAL_PASSWORD` gates the public-facing Influencer Portal section of
  the dashboard — unrelated to admin/API access.
- No agent should get write access to the Obsidian vault beyond a scoped
  subfolder (e.g. `Agent Reports/`) until a review step exists. v0.1 writes
  only to `Agent Reports/` for this reason.
- No real capital, trading, or external message-sending (WhatsApp/SMS/social
  posting) is triggered automatically by this slice. Existing `blotato`
  publish endpoint already requires an explicit POST with real account ID —
  unchanged, not touched by this slice.

## Dependencies

- Python 3.14 (stdlib only — `http.server`, `urllib`, `json`). No new
  third-party packages required for this slice.
- Existing `.env` keys: `OLLAMA_API_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.
- Obsidian vault path: `/Users/tumeloramaphosa/Obsidian/SecondBrain`
  (hardcoded default, overridable via new `.env` key `OBSIDIAN_VAULT_PATH`).

## Acceptance criteria for v0.1 vertical slice

See `task_plan.md` for the full slice definition. Summary: a user clicks
"Ask Brain" in the dashboard with a role + question, the server calls Ollama
Cloud with a role-scoped system prompt, writes the resulting answer as a
timestamped markdown note into `Obsidian/SecondBrain/Agent Reports/`, and
the dashboard displays the same result immediately — proving the full
Dashboard → Agent → Model → Brain → Result path with zero fabricated data.
