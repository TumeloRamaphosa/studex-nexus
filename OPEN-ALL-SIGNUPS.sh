#!/usr/bin/env bash
# Studex Nexus — mass-signup URL opener.
# Opens all free-tier signup pages in your default browser at once.
# Sign up for each with tumelor001@gmail.com (or dedicated per-service alias).
#
# Usage:
#   bash OPEN-ALL-SIGNUPS.sh                  # open all 15
#   bash OPEN-ALL-SIGNUPS.sh cloudflare       # open only Cloudflare
#   bash OPEN-ALL-SIGNUPS.sh top5             # open the 5 highest-priority

set -e
OPEN=""
if command -v open >/dev/null 2>&1; then OPEN="open"        # macOS
elif command -v xdg-open >/dev/null 2>&1; then OPEN="xdg-open"  # linux
elif command -v start >/dev/null 2>&1; then OPEN="start"    # WSL
else echo "Can't find 'open'/'xdg-open'/'start' — copy URLs from below"; fi

declare -a TOP5=(
  "https://dash.cloudflare.com/profile/api-tokens"
  "https://vercel.com/account/tokens"
  "https://huggingface.co/settings/tokens"
  "https://dash.deno.com/account#access-tokens"
  "https://fly.io/app/sign-up"
)

declare -a ALL=(
  # Priority tier — the 5 with the biggest ROI
  "https://dash.cloudflare.com/profile/api-tokens                  # Cloudflare: 100k Workers req/day + unlimited Pages + R2 10GB + D1 5GB + Vectorize + Workers AI"
  "https://vercel.com/account/tokens                                # Vercel: unlimited hobby projects, serverless"
  "https://huggingface.co/settings/tokens                           # HuggingFace: 16GB CPU Space, model hosting, inference"
  "https://dash.deno.com/account#access-tokens                      # Deno Deploy: 1M req/mo, 35+ edge regions"
  "https://fly.io/app/sign-up                                       # Fly.io: 3 VMs/org × 10 orgs = 30 free VMs"

  # DB / KV tier
  "https://supabase.com/dashboard/account/tokens                    # Supabase: 500MB Postgres + 1GB storage"
  "https://console.neon.tech/app/settings/api-keys                  # Neon: 3GB Postgres, 100hrs compute/mo"
  "https://app.turso.tech/settings/tokens                           # Turso: 500 SQLite DBs, 9GB storage"
  "https://console.upstash.com/account/api                          # Upstash: 10k Redis commands/day"

  # Hosting / static tier
  "https://app.netlify.com/user/applications#personal-access-tokens # Netlify: 100GB bandwidth/mo"
  "https://railway.app/account/tokens                               # Railway: \$5 free credit/mo"
  "https://render.com/                                              # Render: 750 hrs/mo web service"

  # DB extras
  "https://cloud.mongodb.com/                                       # MongoDB Atlas: 512MB shared cluster"
  "https://app.planetscale.com/                                     # PlanetScale: 5GB DB"

  # Bonus — try these last
  "https://signup.cloud.oracle.com/                                 # Oracle Cloud (will probably fail — see docs)"
  "https://portal.azure.com/#create/microsoft.azuresponsorsubscription  # Azure Free (12 mo + \$200 credit)"
  "https://aws.amazon.com/free/                                     # AWS Free Tier (12 mo)"
)

if [ "${1:-all}" = "top5" ]; then
  URLS=("${TOP5[@]}")
  echo "Opening top-5 highest-ROI signups..."
elif [ -n "${1:-}" ] && [ "${1:-}" != "all" ]; then
  # Filter to services matching the arg
  URLS=()
  for entry in "${ALL[@]}"; do
    if echo "$entry" | grep -qi "$1"; then
      URLS+=("$(echo "$entry" | awk '{print $1}')")
    fi
  done
else
  URLS=()
  for entry in "${ALL[@]}"; do
    URLS+=("$(echo "$entry" | awk '{print $1}')")
  done
  echo "Opening ALL 16 signup pages. Deep breath."
fi

echo ""
for url in "${URLS[@]}"; do
  echo "  -> $url"
  [ -n "$OPEN" ] && $OPEN "$url" 2>/dev/null || true
  sleep 0.4
done

echo ""
cat <<'HOWTO'

For each tab that opened:
  1. Sign up (or "Log in" if you already have the account) with tumelor001@gmail.com
  2. Verify email if prompted
  3. Navigate to the API token / access token page
  4. Create a token with FULL scope (or the scope shown in the tab)
  5. Copy token → paste into this chat like:
       cloudflare: <token>
       vercel: <token>
       hf: <token>
       ...

Cipher will wire each service the second its token arrives.

TIP: Most services accept the same email. For per-service isolation, use:
     tumelor001+cloudflare@gmail.com
     tumelor001+vercel@gmail.com
     tumelor001+neon@gmail.com
     ...
The "+xxx" suffix all delivers to tumelor001@gmail.com but registers as unique accounts.

HOWTO
