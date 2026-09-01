# Studex Nexus — Monorepo Map

**Superproject:** github.com/TumeloRamaphosa/studex-nexus
**Consolidated:** 2026-09-01
**Mode:** git submodules (safe — every source dir remains intact on disk)

---

## Structure

```
studex-nexus/                                    (superproject, this repo)
├── agents-nest/
│   └── cloud-vm/               → The-Nexus-Agents-NEst           (renamed from SrudEx-Agents-Nest-Cloud-VM)
├── agents/
│   ├── base-agent/             (TypeScript template — to be scaffolded)
│   ├── robusca/                → robusca-brain                   (CAO)
│   └── dr-fixit/               → agents-dr.fixit
├── nexus/
│   ├── mission-control/        → studex-mission-control
│   └── command-center-v0/      → command-center                  (older)
├── platform/
│   ├── valley-os/              → StudEx-Valley-OS
│   ├── mcp-bridge/             (TO BUILD — unifies Base44 + OpenClaw + Hermes + Google + Alibaba + CF + Vercel + Context7 + Honcho + Cursor MCPs)
│   └── bootstrap/              (contains ../agents-nest-landing/gcp-bootstrap.sh)
├── verticals/
│   ├── global-markets/         → Global-Trader
│   └── coffee/                 → Africa-Coffee-Bean
└── labs/
    ├── agentic-lab-v3/         → agentic-lab-v3
    └── dark-factory/           → dark-factory                    (historical)
```

---

## Submodules Live in the Superproject (10)

| Path | Source repo | Branch | Purpose |
|---|---|---|---|
| `agents-nest/cloud-vm` | TumeloRamaphosa/The-Nexus-Agents-NEst | main | The renamed Agents Nest Cloud VM repo |
| `agents/robusca` | TumeloRamaphosa/robusca-brain | main | Robusca CAO agent brain |
| `agents/dr-fixit` | TumeloRamaphosa/agents-dr.fixit | main | Dr Fixit specialist agent |
| `platform/valley-os` | TumeloRamaphosa/StudEx-Valley-OS | claude/plan-repo-integration-fag6C | Valley OS platform layer |
| `nexus/mission-control` | TumeloRamaphosa/studex-mission-control | main | Nexus dashboard mission control |
| `nexus/command-center-v0` | TumeloRamaphosa/command-center | main | Earlier command center (kept for reference) |
| `verticals/global-markets` | TumeloRamaphosa/Global-Trader | main | B2B commodity trading platform |
| `verticals/coffee` | StudEX/Africa-Coffee-Bean | main | Africa Coffee Bean vertical |
| `labs/agentic-lab-v3` | TumeloRamaphosa/agentic-lab-v3 | cursor/dark-factory-scaffold | Experimental agent lab |
| `labs/dark-factory` | TumeloRamaphosa/dark-factory | main | Dark factory (historical) |

---

## Pending Publish (local-only git repos — need GitHub push before submoduling)

| Dir | Reason not yet submoduled | Suggested target path |
|---|---|---|
| `~/studex-command-center` | No git remote (local-only) | `nexus/command-center/` |
| `~/studex-orchestrator` | No commits yet + no remote | `platform/orchestrator/` |
| `~/studex-research-lab` | Local Gitea remote only (localhost:3000) | `labs/research/` |

**To publish each:** `cd <dir> && gh repo create TumeloRamaphosa/<name> --public --push --source=. --remote=origin`

---

## Bare Directories to Import Later (19 — no git init yet)

These dirs have content but no git history. Each should be `git init`'d, first-committed, pushed to a new GitHub repo, then added as a submodule.

Categorized by target monorepo location:

**agents/**
- `~/naledi-os` → `agents/naledi/`

**platform/**
- `~/studex-platform` → `platform/core/`
- `~/studex-hermes-router` → `platform/hermes-router/`
- `~/studex-n8n-workflows` → `platform/n8n/`
- `~/studex-agent-cli` → `platform/cli/`
- `~/studex-integrations` → `platform/integrations/`
- `~/agent-ops` → `platform/agent-ops/` (already git — no remote)

**verticals/**
- `~/studex-global-markets` → `verticals/global-markets/frontend/`
- `~/studex-coffee-agents` → `verticals/coffee/agents/`
- `~/studex-trading-desk` → `verticals/trading-desk/`
- `~/studex-voice` → `verticals/voice/`

**nexus/**
- `~/studex-desktop-app` → `nexus/desktop/` (pick one)
- `~/studex-desktop-apps` → `nexus/desktop-apps/` (or merge with above)

**brain/**
- `~/Studex-Second-Brain` → `brain/` (large — evaluate before importing)

**labs/**
- `~/super-agents` → `labs/super-agents/`
- `~/studex-saas-study` → `labs/saas-study/`
- `~/studex-build` → `labs/build/`
- `~/langgraph_studex` → `labs/langgraph/`

**content/**
- `~/studex_content` → `content/`
- `~/studex-paperclip-page` → `content/paperclip-page/` (already git — no remote)
- `~/studex-email` → `content/email/`
- `~/studex-wave` → `content/wave/`
- `~/studex-dashboard` → `content/dashboard/`

**cloud/**
- `~/studex-cloud` → `platform/cloud/` (0 files — likely empty scaffold, safe to skip)

---

## Not Included (Third-Party Clones on Disk)

These live in `~/` but are open-source projects (not Studex code). Left alone.

- hermes-workspace (outsourc-e)
- hermes-webui (nesquena)
- gbrain (garrytan)
- graphify (safishamsi)
- agent-os (buildermethods)
- context7 (upstash)
- gstack-repo (garrytan)
- cashclaw (ertugrulakben)
- caveman (JuliusBrussee)
- ClawX-repo (ValueCell-ai)
- claude-code-*, claude-skills-* (various)
- dograh, godmode, G0DM0D3, free-claude-code, Agent-Reach, agency-agents
- antigravity-cli (michaelw9999)
- eth-studex-testing (GummyPuppy)

---

## Working With the Monorepo

**Clone with all submodules:**
```
git clone --recurse-submodules https://github.com/TumeloRamaphosa/studex-nexus
```

**Update all submodules to latest:**
```
git submodule update --remote --merge
```

**Add a new submodule:**
```
git submodule add https://github.com/TumeloRamaphosa/<repo>.git <path>
git commit -m "add <name> submodule"
```

**Publish a bare dir and add as submodule:**
```
cd ~/<some-bare-dir>
git init && git add . && git -c user.email=t.ramaphosa@studex.dev commit -m "Initial"
gh repo create TumeloRamaphosa/<name> --public --push --source=. --remote=origin
cd ~/studex-nexus
git submodule add https://github.com/TumeloRamaphosa/<name>.git <target-path>
```
