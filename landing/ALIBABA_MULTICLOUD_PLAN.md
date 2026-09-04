# Alibaba Cloud Multi-Cloud Plan — Studex Nexus

**Companion to:** GCP as primary. Alibaba as parallel fallback + cost-arbitrage layer.
**Prepared:** 2026-09-01
**Alibaba Account ID:** 5229582732143218 (Tumelo, existing hosting account)

---

## Why Alibaba (Strategic Rationale)

- **Africa-friendly pricing.** Compute + egress on Alibaba runs 30-50% cheaper than GCP for equivalent tiers, especially in Frankfurt (eu-central-1) and Dubai (me-east-1), the two closest regions to South Africa.
- **Zero onboarding friction.** Tumelo already has an Alibaba Cloud hosting account with a live payment method. That's weeks saved.
- **BRICS narrative.** Studex is South African. BRICS alignment is a real business signal for enterprise clients and government adjacencies — the same clients that pay premium for POPIA-compliant infrastructure will also value non-US-only sovereignty.
- **Qwen is first-party.** If we use Alibaba's PAI (Platform for AI) service, Qwen 3 / Qwen-Coder / Qwen-Max are native, uncapped, and cheap. We already route to Qwen for cost-tier work.
- **Startup credits.** Alibaba Startup Program (https://www.alibabacloud.com/campaign/startupprogram) typically offers $1,000-$3,000 in initial credits plus 20-40% off standard rates for 12 months. Smaller than Google's but stackable — same product, both credit pools, halved bill.

---

## Service Mapping — GCP → Alibaba

| GCP Service (Studex Nexus uses) | Alibaba Equivalent | Notes |
|---|---|---|
| Cloud Run | **Serverless App Engine (SAE)** or **Function Compute (FC)** | SAE for long-running containers; FC for event-driven |
| Pub/Sub | **Message Queue for Apache RocketMQ** (MQ) | RocketMQ has ordered delivery + DLQ, matches Pub/Sub semantics |
| Firestore (native) | **Tablestore** or **ApsaraDB for MongoDB** | Tablestore for schemaless K/V; MongoDB for richer query |
| Cloud Storage | **Object Storage Service (OSS)** | Direct S3-API-compatible |
| Cloud Functions | **Function Compute (FC)** | HTTP triggers + event source support |
| Artifact Registry | **Container Registry (ACR)** | Enterprise edition recommended |
| Secret Manager | **KMS Secrets Manager** | Rotation supported |
| Cloud Build | **CodePipeline / CI in ACR** | Simpler than GCP Cloud Build for our needs |
| Vertex AI (Gemini) | **PAI-EAS** with Qwen models | Qwen 3 native, first-party |
| Cloud Logging | **SLS (Log Service)** | Powerful query language; retention configurable |
| Eventarc | **EventBridge** | Similar cross-service event routing |
| Cloud Monitoring | **CloudMonitor** | Alarm rules + Grafana integration |

---

## Recommended Region

**Primary Alibaba region: `eu-central-1` (Frankfurt)**

- Best combined latency to South Africa (~145-170ms) and to Europe / MENA
- Full service coverage (SAE, MQ, Tablestore, PAI all available)
- POPIA-compatible under adequacy-based data flow rules (still keep PII on GCP africa-south1 for hard compliance)

**Secondary region: `me-east-1` (Dubai)**

- For MENA-oriented clients
- Backup for Frankfurt in disaster scenarios

**Not recommended:** any ap-* region — too far from Africa for real-time agent operations.

---

## Deployment Model

```
                   Cloudflare DNS + Load Balancer
                            |
        +-------------------+-------------------+
        |                                       |
   GCP africa-south1                    Alibaba Frankfurt
   (Primary — 100% traffic)             (Warm standby + burst)
   |                                    |
   All 10 agents live                   Robusca + General + Naledi
   Nexus dashboard                      replicated
   Firestore = source of truth          Tablestore = read replica
```

**Traffic policy:**
- Normal ops: 100% of dashboard + agent traffic hits GCP africa-south1.
- Cost-arbitrage: bulk background jobs (memory consolidation, weekly digests, RALF loop, batch content generation) route to Alibaba Frankfurt where compute is cheaper.
- Disaster / degraded: Cloudflare failover flips 100% of read + write traffic to Alibaba warm standby within 30 seconds.

**Data policy:**
- POPIA-sensitive customer PII → GCP africa-south1 **only** (Firestore).
- Non-PII computation, aggregate stats, batch output → Alibaba is fair game.
- Obsidian vault → sync both ways to both clouds (git-based), but source of truth remains GCS in GCP.

---

## Ballpark Cost Comparison (10-Agent Baseline)

**Verify from console before committing — 2026 pricing shifts. All figures USD/month estimates.**

| Line item | GCP africa-south1 | Alibaba Frankfurt |
|---|---|---|
| 10 × always-warm containers (small) | ~$450 | ~$280 |
| Message bus (10M msgs/mo) | ~$60 | ~$25 |
| Document DB (20M ops/mo) | ~$90 | ~$50 |
| Object storage (500GB) | ~$25 | ~$12 |
| Egress to SA (100GB/mo) | ~$50 | ~$18 |
| **Baseline monthly** | **~$675** | **~$385** |

Roughly **40% cost savings on Alibaba for equivalent baseline load** — but latency to SA is 3-4× higher than GCP africa-south1. Use Alibaba for computation, not for user-facing chat.

---

## Data Sovereignty Note

Alibaba is subject to PRC jurisdiction and data localization laws in mainland China regions. Frankfurt (eu-central-1) is subject to EU GDPR (and by proxy compatible with POPIA under adequacy). We keep customer PII off Alibaba entirely — Frankfurt included — to eliminate ambiguity. Alibaba runs **stateless computation and non-PII memory only**.

---

## Concrete Next Steps

1. **Log into existing Alibaba Cloud console** → grab account ID and note current region.
2. **Apply for Alibaba Startup Program** → https://www.alibabacloud.com/campaign/startupprogram
3. **Enable services in Frankfurt (eu-central-1):**
   - Serverless App Engine (SAE)
   - Message Queue for RocketMQ
   - Tablestore
   - Object Storage Service (OSS)
   - Container Registry (ACR) — Enterprise
   - Function Compute (FC)
   - PAI-EAS (for Qwen inference)
4. **Provision the 8 message topics on RocketMQ** (mirror the GCP Pub/Sub topic names for parity):
   - studex-commands, studex-agent-output, studex-approvals, studex-escalations, studex-memory-write, studex-war-room, studex-heartbeat, studex-nexus-stream
5. **Set up cross-cloud tunnel** — either Cloudflare Tunnel (already in Studex stack) or a small self-hosted Wireguard peer on both clouds — so agents can address each other by internal hostname regardless of which cloud they live in.
6. **Adapt base-agent code** — introduce a `PubSubAdapter` interface in `src/pubsub.ts` with two implementations: `GcpPubSubAdapter` and `AlibabaRocketMqAdapter`. Same for `MemoryAdapter` (Firestore vs Tablestore) and `StorageAdapter` (GCS vs OSS). Selected at boot time via env var `AGENT_CLOUD=gcp|alibaba`.
7. **Deploy Robusca (CAO) and Naledi (CMO) to Frankfurt as warm standby.** Everything else stays GCP-only until we hit traffic that justifies the extra ops burden.

---

## When to Reassess

Revisit this multi-cloud plan when any of the following triggers fires:

- Monthly GCP bill crosses $2,000 (cost-arbitrage becomes material)
- A single-region GCP outage hits us in production (disaster recovery becomes urgent)
- We land an enterprise / government client that requires non-US-cloud primary hosting (sovereignty becomes contractual)
- Alibaba lands an africa-south region (redesign the whole thing — Alibaba becomes co-primary)

Until one of those fires, treat this doc as the paved road, not the immediate build.
