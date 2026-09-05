# Hermes Button — copy-paste snippet

A ready-to-paste HTML button that opens (or dispatches to) your Hermes agent runtime. Drop it into any Studex page.

Hermes runtime lives at `hermes-webui` container on your Mac (port `8787`) — reachable at:
- Local: `http://localhost:8787`
- Tailnet: `http://<mac-tailscale-ip>:8787`
- Public (once Cloudflare Tunnel is wired): `https://hermes.studex.co.za`

## Snippet 1 — Floating action button (bottom-right)

Paste this into any HTML page's `<body>`. Zero dependencies.

```html
<!-- Hermes floating action button -->
<button id="hermes-btn" onclick="openHermes()" title="Open Hermes agent runtime">
  <span class="hermes-dot"></span> Hermes
</button>
<style>
  #hermes-btn {
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: #eb6834; color: #161615;
    padding: 12px 18px; border-radius: 30px; border: none;
    font: 700 13px/1 ui-monospace, "SF Mono", Menlo, monospace;
    letter-spacing: 0.05em; text-transform: uppercase; cursor: pointer;
    box-shadow: 0 6px 20px rgba(235,104,52,0.4);
    display: flex; align-items: center; gap: 8px;
  }
  #hermes-btn:hover { background: #ffd21e; transform: translateY(-2px); }
  .hermes-dot {
    width: 8px; height: 8px; background: #0ca30c;
    border-radius: 50%; animation: hermes-pulse 1.5s ease-in-out infinite;
  }
  @keyframes hermes-pulse { 50% { opacity: 0.4; } }
</style>
<script>
  const HERMES_URL = 'http://localhost:8787'; // update to https://hermes.studex.co.za once tunnel is live
  function openHermes() { window.open(HERMES_URL, '_blank'); }
</script>
```

## Snippet 2 — Inline dispatch button (send a task, don't open UI)

Use in a specific spot on a page — dashboards, product pages, admin panels. Fires a task at a specific Hermes agent.

```html
<button id="dispatch-btn" onclick="dispatchToHermes()">
  Ask Hermes → Robusca
</button>
<style>
  #dispatch-btn {
    background: transparent; color: #eb6834;
    border: 1px solid #eb6834; padding: 8px 14px; border-radius: 4px;
    font: 600 13px ui-monospace, "SF Mono", Menlo, monospace;
    cursor: pointer;
  }
  #dispatch-btn:hover { background: rgba(235,104,52,0.1); }
</style>
<script>
  const HERMES_URL = 'http://localhost:8787';
  async function dispatchToHermes() {
    const task = prompt('Task for Robusca:');
    if (!task) return;
    try {
      const r = await fetch(`${HERMES_URL}/dispatch`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ agent: 'robusca', task })
      });
      alert(r.ok ? 'Dispatched.' : 'Failed: ' + r.status);
    } catch (e) {
      alert('Hermes unreachable at ' + HERMES_URL);
    }
  }
</script>
```

## Snippet 3 — Multi-agent selector (dropdown + dispatch)

For pages where the user picks which agent to send the task to.

```html
<div id="hermes-picker" style="display:flex;gap:8px;align-items:center;">
  <select id="hermes-agent" style="padding:6px 10px;background:#1e1e1c;color:#fff;border:1px solid #333;border-radius:4px;font:inherit;">
    <option value="robusca">Robusca — Chief of Staff</option>
    <option value="naledi">Naledi — CMO</option>
    <option value="cipher">Cipher — CTO</option>
    <option value="marcus">Marcus — CFO</option>
    <option value="atlas">Atlas — Strategy</option>
    <option value="dr-reeves">Dr Reeves — Research</option>
    <option value="lucius">Lucius Julius — Critic</option>
    <option value="studio">Studio — Design</option>
  </select>
  <input id="hermes-task" placeholder="Task…"
         style="flex:1;padding:6px 10px;background:#1e1e1c;color:#fff;border:1px solid #333;border-radius:4px;font:inherit;min-width:200px;">
  <button onclick="hermesFire()"
          style="padding:6px 12px;background:#eb6834;color:#161615;border:none;border-radius:4px;font:700 12px ui-monospace;cursor:pointer;">
    Dispatch
  </button>
</div>
<script>
  async function hermesFire() {
    const agent = document.getElementById('hermes-agent').value;
    const task = document.getElementById('hermes-task').value.trim();
    if (!task) return alert('Task required');
    const HERMES_URL = 'http://localhost:8787';
    try {
      const r = await fetch(`${HERMES_URL}/dispatch`, {
        method: 'POST', headers: {'content-type':'application/json'},
        body: JSON.stringify({ agent, task })
      });
      const data = await r.json().catch(() => ({}));
      alert(r.ok ? `${agent}: ${JSON.stringify(data)}` : `Failed ${r.status}`);
      document.getElementById('hermes-task').value = '';
    } catch (e) {
      alert('Hermes down. Start with: docker start hermes-webui-hermes-webui-1');
    }
  }
</script>
```

## Where to embed

Already wired into:
- `~/studex-nexus/nexus/skill-marketplace/index.html` (floating button, bottom-right)

Good candidates to add next:
- `~/studex-nexus/nexus/fleet-command/index.html` — one-click dispatch to fleet agents
- Agents Nest landing page (marketing conversion — "Try a live agent")
- Customer portal / admin dashboards

## Hermes's actual API (verified against running instance)

Hermes is a self-hosted chat runtime (multi-provider LLM interface — Claude/OpenAI/DeepSeek/Ollama/etc.). It doesn't have a `/dispatch` endpoint — you dispatch by creating a session with the agent's system prompt, then sending a chat message.

**GET endpoints:**
```
GET  /                              → the Hermes web UI
GET  /health                        → JSON: { status, sessions, active_streams, uptime_seconds }
GET  /api/session                   → session details
GET  /api/sessions                  → list all sessions
GET  /api/list                      → list of profiles/models
GET  /api/chat/stream?stream_id=X   → SSE stream (long-lived — read tokens as they arrive)
GET  /api/file                      → file access
GET  /api/approval/pending          → tool-approval queue
GET  /api/session/worktree/status
```

**POST endpoints:**
```
POST /api/upload
POST /api/session/new               → { title, system_prompt } → { session_id }
POST /api/session/update
POST /api/session/delete
POST /api/chat/start                → { session_id, message } → { stream_id }
POST /api/chat                      → sync version (blocks until done)
POST /api/approval/respond
POST /api/session/worktree/remove
```

**The two-step dispatch pattern** (what the snippets above use — updated):

```js
// 1. Create a session, injecting the agent's Agency .md file as system prompt
const sess = await fetch(`${HERMES_URL}/api/session/new`, {
  method: 'POST', headers: {'content-type':'application/json'},
  body: JSON.stringify({
    title: 'Robusca — sales pipeline audit',
    system_prompt: '<contents of agency-agents/robusca.md>'  // inline
  })
});
const { session_id } = await sess.json();

// 2. Send the task, get back stream_id
const chat = await fetch(`${HERMES_URL}/api/chat/start`, {
  method: 'POST', headers: {'content-type':'application/json'},
  body: JSON.stringify({ session_id, message: 'Audit last week Q4 pipeline movements.' })
});
const { stream_id } = await chat.json();

// 3. Read the SSE stream
const es = new EventSource(`${HERMES_URL}/api/chat/stream?stream_id=${stream_id}`);
es.onmessage = e => console.log(JSON.parse(e.data));
```

## Making it work publicly (Cloudflare Tunnel)

Once Cloudflare token lands:
```
cloudflared tunnel create hermes
cloudflared tunnel route dns hermes hermes.studex.co.za
# add ingress rule: hostname=hermes.studex.co.za, service=http://localhost:8787
cloudflared tunnel run hermes
```

Then update `HERMES_URL` in every snippet from `http://localhost:8787` → `https://hermes.studex.co.za`. Done.
