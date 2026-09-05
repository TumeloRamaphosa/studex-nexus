# Cloudflare — the customer-facing edge

Studex Nexus uses Cloudflare as the always-on public edge. Every customer-facing thing (marketing sites, agent APIs, webhook receivers, tunnels to internal services) sits on Cloudflare's free tier — no signup drama, no card required, no idle-stop.

## What we're using (all free tier)

| Product | Free monthly limit | Studex usage |
|---|---|---|
| **Pages** | Unlimited sites, 500 builds/mo, 100 custom domains | Agents Nest landing, Studex Meat, all marketing sites |
| **Workers** | 100k requests/day (~3M/mo), 10ms CPU per req | MCP bridge routes, webhook receivers, edge APIs |
| **Workers AI** | 10k neurons/day | Free Llama 3.3 + Mistral + embeddings — fallback inference |
| **R2** | 10 GB storage, 1M reads/mo, 10M writes/mo | Agent memory dumps, image storage, log archives |
| **D1** (SQL) | 5 GB, 5M reads/day, 100k writes/day | Agent state, session records, lightweight tables |
| **KV** | 100k reads/day, 1k writes/day | Session tokens, rate limits, config |
| **Vectorize** | 30M queries/mo, 5M stored dimensions | Agent memory embeddings (free ChromaDB alt) |
| **Queues** | 1M messages/mo | Async agent jobs |
| **Tunnel** | Unlimited | Public HTTPS for VM, Mac Mini, Ollama, Gitea — no port forward |
| **Zero Trust Access** | 50 free users | Auth wall on Gitea, n8n, admin panels |
| **Turnstile** | Unlimited | CAPTCHA replacement on signup forms |
| **Email Routing** | Unlimited | Custom addresses on your domains |
| **Images** | 100k stored, 500k transforms/mo | Product photos, agent avatars |
| **Stream** | 1000 min/mo video hosting | Product demos, onboarding videos |

## Directory layout

```
platform/cloudflare/
├── pages/         # Pages projects (marketing sites — one dir per project)
├── workers/       # Workers scripts (MCP router, webhook receivers, edge APIs)
└── tunnel/        # cloudflared config (which local services get public URLs)
```

## Wiring flow (once Cloudflare token is provided)

1. Cipher gets the CF API token
2. Wrangler CLI on this Mac authenticates against it
3. First deploys:
   - Pages project `agents-nest` (deploys from `landing/index.html`)
   - Worker `studex-mcp-router` (skeleton — grows as MCP bridge builds)
   - Tunnel to VM for n8n.studex.co.za + gitea.studex.co.za
4. All future services just `wrangler deploy` from here.

## To provision (waiting on Tumelo)

- [ ] Cloudflare API token pasted
- [ ] Cloudflare Account ID pasted
- [ ] Confirm which domain(s) Cloudflare manages the DNS for (studex.co.za? studex-group.com? .dev?)
