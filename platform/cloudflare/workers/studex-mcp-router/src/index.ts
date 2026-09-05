/**
 * studex-mcp-router — Cloudflare Worker skeleton.
 *
 * Purpose: sit at the edge, route agent requests to backend services
 * (n8n on GCE VM, MCP bridge, per-agent Cloud Run, etc.).
 *
 * Deploy: cd platform/cloudflare/workers/studex-mcp-router && npx wrangler deploy
 */

export interface Env {
  // AI: Ai;                    // Workers AI binding
  // SESSIONS: KVNamespace;     // KV for session tokens
  // AGENT_LOGS: R2Bucket;      // R2 for log dumps
  // STATE: D1Database;         // D1 for agent state
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health probe
    if (url.pathname === "/healthz") {
      return Response.json({
        ok: true,
        service: "studex-mcp-router",
        ts: new Date().toISOString(),
      });
    }

    // Route: /agent/{name}/{action}
    const match = url.pathname.match(/^\/agent\/([^/]+)\/([^/]+)$/);
    if (match) {
      const [, agent, action] = match;
      return Response.json({
        routed_to: agent,
        action,
        note: "handler not wired yet — Cipher will fill this in per agent",
      });
    }

    // Default
    return new Response(
      "Studex Nexus MCP Router — see /healthz or /agent/{name}/{action}",
      { headers: { "content-type": "text/plain" } }
    );
  },
};
