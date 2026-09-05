# Packaging Paid Skills — from Agency Collection to Revenue

**Source pool:** `~/agency-agents/` — 201 specialist agents across 18 divisions.
**Delivery layer:** Cloudflare Workers + Pages (customer-facing) + Hermes (backend runtime) + Paystack (billing).
**Model:** SaaS bundles priced in ZAR, delivered per-tenant with metered usage.

## The play

Agency has 201 free open-source agents. Nobody sells raw skill files — they sell:
1. **Curation** — which 6 agents belong in a "sales team," which 7 make a "security team"
2. **Runtime** — the customer doesn't spin up Docker; they hit an API
3. **Integration** — pre-wired to their WhatsApp, Notion, Gmail, Shopify
4. **Support + updates** — one throat to choke when the agent misbehaves

You charge for the last three. The skill files themselves stay open-source (respects the Agency license).

## The six launch bundles (built into the marketplace)

Already defined in `~/studex-nexus/nexus/skill-marketplace/index.html`:

| Bundle | Tier | Price | Agents | Target buyer |
|---|---|---|---|---|
| **Security Team Pack** | Enterprise | R2,499/mo | 7 | Fintech, exchanges, gov ministries |
| **Growth & Marketing Pack** | SMB | R1,499/mo | 8 | E-commerce, DTC brands |
| **Sales & Deal Desk Pack** | SMB | R1,499/mo | 6 | B2B startups, consulting firms |
| **Engineering Team Pack** | Startup | R2,999/mo | 9 | Solo founders, small dev shops |
| **Design Studio Pack** | SMB | R999/mo | 5 | Agencies, in-house marketing |
| **Agent Lord — Full Access** | Enterprise | R9,999/mo | all 201 | Enterprises, holding cos |

Total addressable price ladder: R999 → R9,999/mo. Covers 4 conversion tiers.

## Example bundle in detail — Security Team Pack

**Composition** (all real files in agency-agents):
- `specialized/blockchain-security-auditor.md` — smart contract + on-chain audits
- `specialized/compliance-auditor.md` — POPIA, SOC2, ISO27001 gap analysis
- `specialized/agentic-identity-trust.md` — identity + trust framework for agent-to-agent auth
- `engineering/engineering-incident-response-commander.md` — pager duty coordinator when things break
- `engineering/engineering-code-reviewer.md` — security-focused code review
- `specialized/automation-governance-architect.md` — governance for automated systems
- `specialized/zk-steward.md` — zero-knowledge proof design + operations

**Customer promise:** "Your on-call security team. 7 specialist agents, always awake, reviewing every deploy, every audit request, every incident. Costs less than one junior security engineer's daily rate."

**Delivered as:**
- One shared Slack/WhatsApp bot per customer (`@studex-security`)
- Weekly automated audit report emailed to CTO
- Slack alert channel for security incidents
- 10 agent-hours/mo included; overage at R150/hr
- White-glove onboarding call in first week (Tumelo or delegate)

**Cost to you at 10 customers × 10 hrs = 100 agent-hrs/mo:**
- Cloudflare Workers: R0 (well inside free tier)
- Model inference (Claude Sonnet avg 30k tokens/hr): 100 × R25 = R2,500/mo
- Hermes/VM overhead: R170/mo
- **Total COGS: ~R2,670/mo → R24,990 MRR → 89% gross margin.**

## How the delivery pipeline works

```
Customer visits studex.co.za/marketplace
    ↓
Selects bundle (e.g. "Security Team Pack — R2,499/mo")
    ↓
Cloudflare Pages checkout → Paystack subscription
    ↓
Paystack webhook → Cloudflare Worker
    ↓ (creates customer tenant)
    - New KV namespace: sessions_<customer_id>
    - New D1 row in tenants table
    - New R2 prefix for their logs
    - New Cloudflare Tunnel subdomain: <customer>.studex.co.za (optional)
    ↓
Hermes gets provisioning event → loads the 7 skill .md files
into a namespaced context for this customer only
    ↓
Customer receives:
    - Login URL: <customer>.studex.co.za
    - API key
    - Slack/WhatsApp bot invite
    ↓
All customer requests → Cloudflare Worker →
    checks API key → checks bundle entitlements →
    routes to Hermes → routes to correct agent →
    returns result → meters usage in D1
    ↓
Monthly: cron worker generates usage report, bills overages via Paystack
```

Every piece of this runs on your existing Cloudflare + GCE VM + Hermes stack. Zero net new infra.

## Legal / licensing checklist

Before shipping the marketplace publicly:

- [ ] **Check Agency's license** (LICENSE file in `~/agency-agents/`) — most permissive licenses allow commercial resale of derivatives; some require attribution. Verify per-agent.
- [ ] **Attribution page** — one page on studex.co.za crediting "Powered by open-source agents from the Agency collection" with a link.
- [ ] **Rewrite descriptions** — don't copy Agency's descriptions verbatim on your marketplace pages; write your own so you're not just reselling their content, you're selling curation + delivery.
- [ ] **Terms of Service** — customer is buying access to your platform + curation, not the agent files themselves. Reserves your right to swap out underlying agents.
- [ ] **Privacy Policy** — you are processing customer data through third-party LLMs. Disclose which providers (Claude, OpenAI, Cloudflare Workers AI).
- [ ] **POPIA compliance** — for SA customers, keep PII in africa-south1 (GCE VM Firestore or Cloudflare EU). Never egress PII to US regions.
- [ ] **DPA (Data Processing Agreement)** — required for any enterprise customer. Have a template ready.

## Pricing psychology — why these numbers

- **R999** — impulse-purchase threshold for SA SMBs. Below the "need finance approval" barrier.
- **R1,499** — matches Studex Empire tier from your existing landing. Consistent price ladder.
- **R2,499** — anchored to "one full-time junior salary is R25k/mo, this is 10%". Easy business case.
- **R2,999** — engineering pack costs more than sales pack because engineering teams have higher tolerance for tool spend.
- **R9,999** — Agent Lord tier ends in 9s deliberately: reads as R10k, but the 9 keeps the tier separate. Enterprise buyers negotiate down from R14,999 quotes; this one is take-it-or-leave-it.

## Rollout sequence (recommended)

**Week 1 — soft launch**
1. Marketplace page live at studex.co.za/marketplace (deploy to Cloudflare Pages)
2. Only Security Team Pack + Design Studio Pack available (2 bundles, less complexity)
3. Paystack test mode
4. Announce to 10 warm contacts in ZATech Slack + WhatsApp

**Week 2 — 3 more bundles**
1. Growth, Sales, Engineering packs go live
2. Paystack live mode
3. First paying customer — you personally onboard them

**Month 2 — Agent Lord tier + white-label**
1. Full-access tier
2. White-label option (customer's brand instead of Studex)
3. Reseller program (agencies get 30% recurring)

**Month 3 — self-serve everything**
1. Removes Tumelo from onboarding loop entirely
2. Automated welcome sequence via AgentMail
3. Video onboarding replaces calls

## Tracking what to build next

Add these bundles once demand signals arrive:
- **Legal Ops Pack** (5 agents) — R1,999/mo — bundle: legal-client-intake, legal-billing-time-tracking, legal-document-review, compliance-auditor, contract-analyzer
- **HR Pack** (4 agents) — R999/mo — hr-onboarding, recruitment-specialist, corporate-training-designer, employee-experience
- **Finance Ops Pack** (5 agents) — R1,499/mo — finance division has 5 agents already, bundle all
- **Game Studio Pack** (20 agents) — R2,999/mo — entire game-development division (blender/godot/unity/unreal/roblox)
- **Africa Vertical Packs** — Meat, Coffee, Wheat, Wildlife (bundle Studex-specific + Agency agents)

## Measuring success

North-star metric: **ARR / month #1 target: R30,000** (12 subscribers avg R2,500).
Leading indicators: bundle-page views, checkout starts, first-agent-run time-to-value.

Instrument with Cloudflare Analytics Engine (free 10M writes/day) — no Google Analytics needed.
