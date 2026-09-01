# Plan: STUDX Daily Tracker OS v0.1 — First Vertical Slice

**Branch**: N/A (working directly in `studex-nexus`, no VCS history yet)
**Status**: Active

## Goal

Prove the full path `Dashboard → Agent → Local/Cloud Model → Brain → Result`
end-to-end with real systems only (no mocked/random data), inside the
existing `studex-nexus` server, before any wider STUDX Alpha buildout.

## Acceptance Criteria

- [ ] A user can open the Nexus dashboard, pick an agent role and type a
      question into a new "Ask Brain" control, and submit it.
- [ ] The server calls Ollama Cloud (existing `server/connectors/ollama.py`)
      with a role-scoped system prompt built from the chosen role.
- [ ] The model's answer is written as a new timestamped markdown file into
      `Obsidian/SecondBrain/Agent Reports/` (real file on disk, not a log
      line) — this is the "Brain" write.
- [ ] The same answer is returned to the browser and rendered in the
      dashboard without requiring a page reload — this is the "Result".
- [ ] If Ollama is unreachable or the vault path is missing, the UI shows a
      real error state (not a silently fabricated success).

## Slices

### Slice 1: Ask Brain — one role, one question, one real Obsidian note

**Value**: Actor = Tumelo (or any dashboard user). Trigger = submitting the
"Ask Brain" form. Observable outcome = a new file appears in
`Agent Reports/` in Obsidian, and its content appears in the dashboard
response panel.
**Path**: Browser form → `POST /api/brain/ask` → `server/app.py` handler →
`server/connectors/ollama.chat()` (existing) → `server/brain.py` (new,
writes markdown file) → JSON response → `app.js` renders result.
**Class**: Behavior change.
**Delivery**: Single PR-equivalent commit (no PR/VCS remote configured yet
for this repo — see Findings; commit locally on request).
**Required implementation skills**: none beyond direct implementation —
this repo has no test harness yet (stdlib-only, no pytest configured); see
"Testing approach" below for how this slice is verified without one.
**Acceptance criteria**:
  1. `POST /api/brain/ask` with `{"role": "Chief of Staff", "question": "..."}`
     returns `200` with `{"answer": "...", "notePath": "Agent Reports/....md"}`
     when Ollama is reachable.
  2. The file at `notePath` exists under the real Obsidian vault and its
     content matches `answer`.
  3. If `OLLAMA_API_KEY` is missing/invalid or the vault path doesn't exist,
     the endpoint returns a non-200 with a real error message — never a
     fabricated 200.
  4. The dashboard's new "Ask Brain" panel calls this endpoint, shows a
     loading state, then renders the returned answer or the real error.
**RED/verification plan (no pytest harness present)**: verify manually with
`curl` against the running server for the success path (real Ollama call,
real file write, inspect file contents on disk) and for the failure path
(temporarily unset `OLLAMA_API_KEY` in a throwaway env, confirm non-200 and
no file written). Record exact commands + output in `progress.md`.
**PR-ready when**: all 4 acceptance criteria above are demonstrated with
real command output pasted into `progress.md`, and the user has clicked
through the dashboard once and confirmed the result appears.

## Explicitly out of scope for v0.1

- Any of the 4-VM topology, MCP layer, model router, Buzz, MiroFish,
  AutoResearch, Agency Agents, investment engine, or event bus. These stay
  as recorded direction in `findings.md` and `ARCHITECTURE.md` until
  independently planned and verified, one piece at a time.
- Notion, Orgo, FeedHive, Freepik connectors — tracked separately, not
  blocking this slice.
- Multi-agent roles beyond a hardcoded role list (no dynamic agent registry
  yet).

## Pre-completion checklist

1. Manual verification commands run and output captured in `progress.md`.
2. `.env` still gitignored, no secret values pasted anywhere in committed
   files.
3. Human (Tumelo) confirms the dashboard "Ask Brain" flow visually before
   this slice is marked complete.
