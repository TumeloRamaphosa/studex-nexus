# Bridge Setup — External Access to Internal Services

## Cloudflare Tunnel for Gitea (100.95.66.29:3000)

**Why:** Any agent NOT on the Tailnet — Cloud Run services, GitHub Actions, hosted MCP servers, ChatGPT/Claude plugins — needs a public HTTPS URL to reach your Gitea. Cloudflare Tunnel gives you that with zero open ports.

### Option A — Quick Tunnel (5 seconds, throwaway URL)

Rotating URL, dies when the process exits. Good for a live demo. Run in a terminal on the machine that can reach Gitea (i.e. any tailnet device):

```
cloudflared tunnel --url http://100.95.66.29:3000
```

Prints something like `https://<random>.trycloudflare.com` — use that as the Gitea URL until you kill the process.

### Option B — Named Tunnel (persistent URL, recommended)

Persistent, tied to a Cloudflare account + domain. Survives reboots. Free.

**One-time setup:**

```
# 1. Log in (opens browser)
cloudflared tunnel login

# 2. Create the tunnel
cloudflared tunnel create studex-gitea

# 3. Route it to a subdomain on a Cloudflare-managed domain
cloudflared tunnel route dns studex-gitea gitea.studex.co.za

# 4. Write the config
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml <<EOF
tunnel: studex-gitea
credentials-file: ~/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: gitea.studex.co.za
    service: http://100.95.66.29:3000
  - service: http_status:404
EOF

# 5. Run it (foreground for test)
cloudflared tunnel run studex-gitea

# 6. Once verified, install as launchd service (Mac):
sudo cloudflared service install
```

**External agents then clone with:**

```
git clone https://gitea.studex.co.za/tumelo/robusca-memory.git
```

### Security Notes

- **Gitea auth:** if the repos are public in Gitea, they're public through the tunnel too. Turn on `SERVICE.REQUIRE_SIGNIN_VIEW = true` in Gitea's `app.ini` to force auth.
- **Cloudflare Access:** wrap the tunnel with Cloudflare Zero Trust Access to require Google/email login before anyone can even see Gitea — free for < 50 users.
- **Never expose Gitea admin:** set `LFS_START_SERVER = false` and disable registration if you don't need it.

## Alternative — Push Mirror Pattern (used for studx-os)

For a single repo that needs to be public + globally reachable, easier: set up a Gitea → GitHub push mirror.

**In Gitea:** repo → Settings → Mirror Settings → Push Mirror → GitHub URL + PAT with `repo` scope.
**On GitHub:** repo appears + auto-updates on every Gitea push.

This is how `platform/studx-os` submodule works today.

**Use the tunnel when:** you have many private repos and want them all reachable without individual mirrors.
**Use push mirror when:** just 1-3 repos need public GitHub presence.

## Tailnet Reference

- `100.95.66.29` = macbook-pro-5 (self) — Gitea host
- Full tailnet: run `tailscale status` for current list
