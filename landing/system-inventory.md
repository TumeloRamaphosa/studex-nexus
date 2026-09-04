# Studex Nexus — System Inventory
**Generated:** 2026-08-31 23:59 SAST
**Machine:** MacBook (darwin-arm64)

---

## 🐳 Docker Containers (31 running)

### Studex Core Stack
| Container | Status | Ports |
|-----------|--------|-------|
| gitea | ✅ Up 5 days | `:3030` → 3000, `:2222` → 22 |
| huly_v7-nginx | ✅ Up 5 days | `:8087` → 80 |
| huly_v7-front | ✅ Up 5 days | `:8080` |
| huly_v7-kvs | ✅ Up 5 days | `:8094` |
| huly_v7-rekoni | ✅ Up 5 days | `:4004` |
| huly_v7-transactor | ✅ Up 5 days | `:8080` |
| huly_v7-fulltext | ✅ Up 5 days | `:4700` |
| huly_v7-workspace | ✅ Up 5 days | |
| huly_v7-collaborator | ✅ Up 5 days | `:3078` |
| huly_v7-account | ✅ Up 5 days | `:3000` |
| huly_v7-stats | ✅ Up 5 days | `:4900` |
| huly_v7-cockroach | ✅ Up 3 days | `:8080`, `:26257` |
| huly_v7-minio | ✅ Up 5 days | `:9000` |
| huly_v7-elastic | ✅ Up 5 days | `:9200`, `:9300` |

### Agent Ops
| Container | Status | Ports |
|-----------|--------|-------|
| agent-ops-perf-monitor | ✅ Up 5 days (healthy) | |
| agent-ops-buzz-agents | ✅ Up 5 days (healthy) | |
| agent-ops-discord-agents | ✅ Up 5 days (healthy) | |
| agent-ops-valley-agents | ✅ Up 5 days (healthy) | |
| agent-ops-katya-bridge | ✅ Up 5 days (healthy) | |
| agent-ops-n8n | ✅ Up 5 days (healthy) | `:5678` |
| hermes-webui-hermes-webui-1 | ✅ Up 28h (healthy) | `:8787` |

### Other
| Container | Status | Ports |
|-----------|--------|-------|
| open-webui | ✅ Up 3 days (healthy) | `:3001` → 8080 |
| open-design | ✅ Up 5 days (healthy) | `:7456` |
| listmonk-db-1 | ✅ Up 5 days (healthy) | `:5432` |
| listmonk-app-1 | ⚠️ Restarting | |

### k3s Cluster
| Container | Status |
|-----------|--------|
| k8s_local-path-provisioner | ✅ Up 5 days |
| k8s_coredns | ✅ Up 5 days |

### Docker Networks
- `agent-ops` (bridge)
- `huly_v7_huly_net` (bridge)
- `multica_default` (bridge)
- `open-design_default` (bridge)
- `hermes-webui_default` (bridge)

---

## 🌐 Network Services

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Gitea** | `:3030` | localhost:3030 | ✅ LISTEN |
| **Huly Front** | `:8087` | localhost:8087 | ✅ LISTEN |
| **n8n** | `:5678` | localhost:5678 | ✅ LISTEN |
| **Ollama** | `:11434` | localhost:11434 | ✅ LISTEN |
| **ControlCenter** | `:7000` | localhost:7000 | ✅ LISTEN |
| **ControlCenter** | `:5000` | localhost:5000 | ✅ LISTEN |
| **OrbStack** | `:32222` | localhost:32222 | ✅ LISTEN |
| **OrbStack API** | `:52432` | localhost:52432 | ✅ LISTEN |
| **ClawX** | `:18789` | localhost:18789 | ✅ LISTEN |

### Agent Dev Ports (OpenCode)
| Instance | Port |
|----------|------|
| OpenCode #1 | `:4001` |
| OpenCode #2 | `:4002` |
| OpenCode #3 | `:4003` |

---

## 🤖 AI Agents & Tools Running

| Agent | Process | Port | Status |
|-------|---------|------|--------|
| **Antigravity IDE** | Antigravi (PID 4600) | :59742, :59744, :59917, :60087 | ✅ Running |
| **ClawX** | ClawX (PID 76821) | :18789, :18791, :18792 | ✅ Running |
| **Mavis (MiniMax)** | minimax (PID 1742) | :49485 | ✅ Running |
| **OpenCode** | opencode (PID 69960-69963) | :4001-4003 | ✅ Running |
| **See-Claude** | node (PID 1008) | — | ✅ Running |
| **LM Studio** | LM Stu (PID 11307) | :41343 | ✅ Running |
| **Discord** | Discord (PID 1702) | :6463 | ✅ Running |
| **Ollama Server** | ollama (PID 56362) | :11434 | ✅ Running |
| **llama-server** | (PID 59735) | :58294 | ⚡ Active inference |

---

## 🧠 Ollama Models

```
qwen2.5:14b              9.0 GB    General coding + reasoning
qwen2.5-coder:7b        4.7 GB    Fast code generation
llama3.2:1b             1.3 GB    Lightweight tasks
kimi-k2.6:cloud         API       Orgo.ai VM
nemotron-3-super:cloud  API       Orgo.ai VM
```

---

## 📁 Key Repos & Projects

| Path | Purpose |
|------|---------|
| `~/skunk-works/vm/` | Skunk Works VM — synced 6 repos |
| `~/agents-nest-landing/` | Agents Nest landing page + webhook |
| `~/Desktop/USB-BUNDLE/` | Dark Factory (713MB) |
| `~/Projects/hermes-usb-portable/` | Hermes portable agent |
| `~/Projects/prime-agent/` | PrimeIntellect RLM agent |
| `~/Projects/orca/` | Orca agent IDE |
| `~/Projects/platform/` | Huly platform |
| `~/Projects/herdr/` | Herdr agent runtime |
| `~/Projects/kit/` | SvelteKit |
| `~/Projects/huly-selfhost/` | Huly self-hosted docker |

---

## ⚠️ Issues

| Item | Status | Notes |
|------|--------|-------|
| listmonk-app-1 | ⚠️ Restarting | Container keeps restarting (50s cycle) |
| OrbStack Port :9000 | ℹ️ Exposed | MinIO and OrbStack both on :9000 — check conflict |
| LaCie Drive | ❌ Not mounted | Physical drive not detected — verify connection |

---

## 🚀 Quick Access URLs

```
Gitea:         http://localhost:3030
Huly:          http://localhost:8087
n8n:           http://localhost:5678
Hermes WebUI:  http://localhost:8787
Open WebUI:    http://localhost:3001
Agent Fleet:   file:///Users/tumeloramaphosa/skunk-works/vm/fleet-manager.html
```
