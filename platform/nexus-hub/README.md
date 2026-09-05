# Nexus Hub — the always-on brain

**Runs on:** `studex-nexus-hub` GCE VM  ·  `34.35.82.49`  ·  `africa-south1-a`  ·  `gen-lang-client-0728429584`

## What lives here

- **n8n** (5678) — workflow engine + cron dispatcher for the whole fleet
- **PostgreSQL** — n8n's persistence layer
- **Watchtower** — auto-updates all containers every hour
- **Cloudflared** — Cloudflare Tunnel client, exposes services publicly without opening ports
- **Uptime Kuma** (3001) — monitors every fleet service, sends alerts on downtime

## Bring it up

```bash
# From your Mac
gcloud compute ssh studex-nexus-hub --project=gen-lang-client-0728429584 --zone=africa-south1-a

# On the VM
sudo apt-get install -y git
sudo git clone https://github.com/TumeloRamaphosa/studex-nexus.git /opt/studex-nexus
cd /opt/studex-nexus/platform/nexus-hub
sudo cp .env.example .env
sudo nano .env       # fill in the 3 secrets

# Generate the two random ones:
sudo bash -c "sed -i.bak \"s|^N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)|\" .env"
sudo bash -c "sed -i.bak \"s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -base64 24)|\" .env"

# For CLOUDFLARE_TUNNEL_TOKEN — get from Cloudflare Zero Trust dashboard,
# then paste it into .env manually.

sudo docker compose up -d
sudo docker compose ps
```

Once up:

- Local: `http://34.35.82.49:5678` → n8n first-run screen
- Public (after Cloudflare Tunnel wired): `https://n8n.studex.co.za`
- Uptime: `http://34.35.82.49:3001`

## Adding more services

Any 24/7 service belongs here. Add to `docker-compose.yml` and `sudo docker compose up -d` again. Candidates:
- **MCP Bridge** — the multi-vendor MCP router
- **Ollama** — local model server on Tailscale
- **Robusca memory daemon** — background embedding + consolidation
- **Base44 → Notion webhook receiver**
- **RALF cron container** — the midnight SAST loop
