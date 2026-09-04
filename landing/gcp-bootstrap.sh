#!/usr/bin/env bash
#
# STUDEX NEXUS — GCP BOOTSTRAP
# Provisions the Google Cloud foundation for Agents Nest:
#   project, billing link, APIs, Firestore, GCS, Artifact Registry,
#   8 Pub/Sub topics, service account, IAM, Secret Manager shells.
#
# Default is DRY-RUN. Pass --execute to actually run.
#
# Usage:
#   ./gcp-bootstrap.sh [--project-id ID] [--region REGION]
#                      [--billing-account ID] [--account EMAIL]
#                      [--dry-run | --execute]
#
set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────────
PROJECT_ID="studex-nexus"
REGION="africa-south1"
BILLING_ACCOUNT=""
ACCOUNT="tumelor001@gmail.com"
MODE="dry-run"

# ─── TTY-aware color logging ─────────────────────────────────────────────────
if [ -t 1 ]; then
  C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_INFO=$'\033[36m'; C_BOLD=$'\033[1m'; C_RESET=$'\033[0m'
else
  C_OK=""; C_WARN=""; C_ERR=""; C_INFO=""; C_BOLD=""; C_RESET=""
fi

log_ok()   { printf '%s[OK]%s   %s\n'   "$C_OK"   "$C_RESET" "$*"; }
log_warn() { printf '%s[WARN]%s %s\n' "$C_WARN" "$C_RESET" "$*"; }
log_err()  { printf '%s[ERR]%s  %s\n'  "$C_ERR"  "$C_RESET" "$*" 1>&2; }
log_info() { printf '%s[..]%s   %s\n'   "$C_INFO" "$C_RESET" "$*"; }
step()     { printf '\n%s[%s]%s %s\n' "$C_BOLD" "$1" "$C_RESET" "$2"; }

# ─── Banner ──────────────────────────────────────────────────────────────────
print_banner() {
  cat <<'BANNER'

  ==========================================================
   STUDEX NEXUS — GCP BOOTSTRAP
   Provisions billable Google Cloud resources
   Read the script before running with --execute
  ==========================================================

BANNER
}

# ─── Usage ───────────────────────────────────────────────────────────────────
usage() {
  cat <<USAGE
Studex Nexus GCP bootstrap.

USAGE:
  $(basename "$0") [OPTIONS]

OPTIONS:
  --project-id ID          GCP project id             (default: studex-nexus)
  --region REGION          Deploy region              (default: africa-south1)
  --billing-account ID     Billing account to link    (optional)
  --account EMAIL          gcloud account to require  (default: tumelor001@gmail.com)
  --dry-run                Print gcloud commands, run nothing (DEFAULT)
  --execute                Actually run gcloud commands (requires confirmation)
  --help                   Show this help

EXAMPLES:
  # Preview what would happen:
  $(basename "$0") --project-id studex-nexus

  # Actually provision (requires billing account for API activation):
  $(basename "$0") --project-id studex-nexus \\
                   --billing-account 0X0X0X-0X0X0X-0X0X0X \\
                   --execute

USAGE
}

# ─── Parse args ──────────────────────────────────────────────────────────────
while [ $# -gt 0 ]; do
  case "$1" in
    --project-id)       PROJECT_ID="$2"; shift 2 ;;
    --region)           REGION="$2"; shift 2 ;;
    --billing-account)  BILLING_ACCOUNT="$2"; shift 2 ;;
    --account)          ACCOUNT="$2"; shift 2 ;;
    --dry-run)          MODE="dry-run"; shift ;;
    --execute)          MODE="execute"; shift ;;
    --help|-h)          usage; exit 0 ;;
    *)                  log_err "Unknown flag: $1"; usage; exit 2 ;;
  esac
done

print_banner
log_info "Mode:          $MODE"
log_info "Account:       $ACCOUNT"
log_info "Project:       $PROJECT_ID"
log_info "Region:        $REGION"
log_info "Billing:       ${BILLING_ACCOUNT:-<not provided>}"

# ─── gcloud runner (dry-run aware) ───────────────────────────────────────────
run() {
  if [ "$MODE" = "dry-run" ]; then
    printf '  %s$%s %s\n' "$C_INFO" "$C_RESET" "gcloud $*"
    return 0
  fi
  gcloud "$@"
}

# In dry-run we don't want lookup calls (like describe) to fail the script.
run_lookup() {
  if [ "$MODE" = "dry-run" ]; then
    printf '  %s$%s %s   %s(lookup — assumed missing in dry-run)%s\n' "$C_INFO" "$C_RESET" "gcloud $*" "$C_WARN" "$C_RESET"
    return 1
  fi
  gcloud "$@" >/dev/null 2>&1
}

# ─── Preflight: gcloud binary + active account ───────────────────────────────
step "0" "Preflight"
if ! command -v gcloud >/dev/null 2>&1; then
  log_err "gcloud not on PATH. Install: https://cloud.google.com/sdk/docs/install"
  exit 1
fi
log_ok "gcloud found: $(gcloud --version | head -1)"

ACTIVE_ACCOUNT="$(gcloud config get-value account 2>/dev/null || true)"
if [ "$ACTIVE_ACCOUNT" != "$ACCOUNT" ]; then
  log_err "Active gcloud account is '$ACTIVE_ACCOUNT'. Expected '$ACCOUNT'."
  log_info "Fix with:"
  printf '    gcloud auth login %s\n' "$ACCOUNT"
  printf '    gcloud auth application-default login\n'
  printf '    gcloud config set account %s\n' "$ACCOUNT"
  exit 1
fi
log_ok "Active account matches: $ACCOUNT"

# ─── Confirmation gate (execute mode only) ───────────────────────────────────
if [ "$MODE" = "execute" ]; then
  printf '\n%s' "$C_WARN"
  cat <<CONFIRM
!!! You are about to provision billable resources !!!
    Project:  $PROJECT_ID
    Account:  $ACCOUNT
    Region:   $REGION
CONFIRM
  printf '%s' "$C_RESET"
  read -r -p 'Type "yes" to continue: ' CONFIRM_INPUT
  if [ "$CONFIRM_INPUT" != "yes" ]; then
    log_warn "Aborted by user."
    exit 0
  fi
fi

# ─── 1. Create or reuse project ──────────────────────────────────────────────
step "1/12" "Create or reuse project '$PROJECT_ID'"
if run_lookup projects describe "$PROJECT_ID"; then
  log_ok "Project already exists."
else
  run projects create "$PROJECT_ID" --name="Studex Nexus" \
    || { log_err "Project create failed. Choose a different --project-id."; exit 1; }
  log_ok "Project created."
fi

# ─── 2. Set active project ───────────────────────────────────────────────────
step "2/12" "Set active project"
run config set project "$PROJECT_ID"
log_ok "Active project: $PROJECT_ID"

# ─── 3. Link billing (or warn) ───────────────────────────────────────────────
step "3/12" "Link billing account"
if [ -n "$BILLING_ACCOUNT" ]; then
  run beta billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT" \
    || log_warn "Billing link failed (may already be linked or IAM missing)."
  log_ok "Billing linked: $BILLING_ACCOUNT"
else
  log_warn "No --billing-account provided. API activation will fail without billing."
  log_info "Link manually: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
fi

# ─── 4. Enable APIs ──────────────────────────────────────────────────────────
step "4/12" "Enable APIs"
APIS=(
  run.googleapis.com
  pubsub.googleapis.com
  firestore.googleapis.com
  cloudfunctions.googleapis.com
  cloudbuild.googleapis.com
  artifactregistry.googleapis.com
  secretmanager.googleapis.com
  iam.googleapis.com
  iamcredentials.googleapis.com
  serviceusage.googleapis.com
  eventarc.googleapis.com
  logging.googleapis.com
  monitoring.googleapis.com
)
run services enable "${APIS[@]}" || log_warn "Some APIs may not have enabled cleanly."
log_ok "APIs enabled: ${#APIS[@]} services."

# ─── 5. Firestore ────────────────────────────────────────────────────────────
step "5/12" "Create Firestore (native mode) in $REGION"
if run_lookup firestore databases describe --database='(default)'; then
  log_ok "Firestore default database already exists."
else
  run firestore databases create --location="$REGION" --type=firestore-native \
    || log_warn "Firestore create failed (may already exist in another region)."
  log_ok "Firestore created."
fi

# ─── 6. GCS bucket for Obsidian vault ────────────────────────────────────────
step "6/12" "Create GCS bucket for Obsidian vault sync"
BUCKET="${PROJECT_ID}-obsidian-vault"
if run_lookup storage buckets describe "gs://${BUCKET}"; then
  log_ok "Bucket already exists: gs://${BUCKET}"
else
  run storage buckets create "gs://${BUCKET}" \
    --location="$REGION" \
    --uniform-bucket-level-access \
    || log_warn "Bucket create failed."
  log_ok "Bucket created: gs://${BUCKET}"
fi

# ─── 7. Artifact Registry (Docker) ───────────────────────────────────────────
step "7/12" "Create Artifact Registry Docker repo 'studex-agents'"
if run_lookup artifacts repositories describe studex-agents --location="$REGION"; then
  log_ok "Artifact Registry repo already exists."
else
  run artifacts repositories create studex-agents \
    --repository-format=docker \
    --location="$REGION" \
    --description="Studex Nexus agent container images" \
    || log_warn "Repo create failed."
  log_ok "Repo created: $REGION-docker.pkg.dev/$PROJECT_ID/studex-agents"
fi

# ─── 8. Pub/Sub topics ───────────────────────────────────────────────────────
step "8/12" "Create Pub/Sub topics (8)"
TOPICS=(
  studex-commands
  studex-agent-output
  studex-approvals
  studex-escalations
  studex-memory-write
  studex-war-room
  studex-heartbeat
  studex-nexus-stream
)
for t in "${TOPICS[@]}"; do
  if run_lookup pubsub topics describe "$t"; then
    log_ok "Topic exists: $t"
  else
    run pubsub topics create "$t" || log_warn "Topic create failed: $t"
    log_ok "Topic created: $t"
  fi
done

# ─── 9. Service account + IAM ────────────────────────────────────────────────
step "9/12" "Create runtime service account + IAM bindings"
SA_NAME="studex-agent-runtime"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if run_lookup iam service-accounts describe "$SA_EMAIL"; then
  log_ok "Service account already exists: $SA_EMAIL"
else
  run iam service-accounts create "$SA_NAME" \
    --display-name="Studex Agent Runtime" \
    --description="Runs Studex Nexus agent Cloud Run services" \
    || log_warn "Service account create failed."
  log_ok "Service account created: $SA_EMAIL"
fi

ROLES=(
  roles/pubsub.publisher
  roles/pubsub.subscriber
  roles/datastore.user
  roles/storage.objectUser
  roles/secretmanager.secretAccessor
  roles/logging.logWriter
)
for role in "${ROLES[@]}"; do
  run projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$role" \
    --condition=None \
    >/dev/null 2>&1 || log_warn "Role bind failed: $role"
  log_ok "Bound: $role"
done

# ─── 10. Service account key ─────────────────────────────────────────────────
step "10/12" "Generate service account key"
mkdir -p ./secrets
if [ ! -f ./secrets/.gitignore ]; then
  printf '*\n!.gitignore\n' > ./secrets/.gitignore
  log_ok "Wrote ./secrets/.gitignore"
fi
KEY_PATH="./secrets/${SA_NAME}.json"
if [ -f "$KEY_PATH" ]; then
  log_warn "Key already exists at $KEY_PATH — skipping (delete + rerun to rotate)."
else
  run iam service-accounts keys create "$KEY_PATH" \
    --iam-account="$SA_EMAIL" \
    || log_warn "Key create failed."
  if [ -f "$KEY_PATH" ]; then
    chmod 600 "$KEY_PATH"
    log_ok "Key written: $KEY_PATH (chmod 600)"
    log_warn "This key is a credential. NEVER commit ./secrets/ to git."
  fi
fi

# ─── 11. Secret Manager shells (empty, ready for values) ─────────────────────
step "11/12" "Create Secret Manager secret shells"
SECRETS=(
  AGENTMAIL_API_KEY
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  NOTION_API_KEY
  BLOTATO_API_KEY
  PAYSTACK_SECRET_KEY
  TAILSCALE_AUTHKEY
)
for s in "${SECRETS[@]}"; do
  if run_lookup secrets describe "$s"; then
    log_ok "Secret exists: $s"
  else
    run secrets create "$s" --replication-policy=automatic \
      || log_warn "Secret create failed: $s"
    log_ok "Secret created (empty): $s"
    log_info "Add a version with:  gcloud secrets versions add $s --data-file=-"
  fi
done

# ─── 12. Summary ─────────────────────────────────────────────────────────────
step "12/12" "Summary"
cat <<SUMMARY

  Provisioned (or verified):
    - Project:            $PROJECT_ID
    - Region:             $REGION
    - Firestore:          native, in $REGION
    - GCS bucket:         gs://${PROJECT_ID}-obsidian-vault
    - Artifact Registry:  $REGION-docker.pkg.dev/$PROJECT_ID/studex-agents
    - Pub/Sub topics:     ${#TOPICS[@]}
    - Service account:    $SA_EMAIL
    - IAM roles:          ${#ROLES[@]}
    - Secret shells:      ${#SECRETS[@]} (fill values with 'gcloud secrets versions add ...')

  Still requires manual action:
    1. Link billing account (if not provided): https://console.cloud.google.com/billing?project=$PROJECT_ID
    2. Apply for Google for Startups credits:  https://cloud.google.com/startup
    3. Fill in each Secret Manager value:      gcloud secrets versions add <NAME> --data-file=-
    4. (Optional) Enable Cloud Domains and buy agentsnest.studex.co.za redirect
    5. Register Google Cloud Skills Boost:     https://www.cloudskillsboost.google (for dev badge)

  Ship the first agent:
    gcloud run deploy studex-robusca \\
      --source=./agents/robusca \\
      --region=$REGION \\
      --service-account=$SA_EMAIL \\
      --no-allow-unauthenticated \\
      --set-env-vars="AGENT_ID=robusca,AGENT_ROLE=CAO,MODEL=claude-sonnet-4-6,PROJECT_ID=$PROJECT_ID,REGION=$REGION"

SUMMARY

if [ "$MODE" = "dry-run" ]; then
  log_warn "DRY RUN — nothing was actually created. Rerun with --execute to provision."
else
  log_ok "Bootstrap complete."
fi

# vim: set ft=bash:
