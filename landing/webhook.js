/**
 * AgentMail Webhook Handler
 * POST /webhook/agentmail — receives { from, to, subject, body }
 * Logs to console and writes to JSON log file
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const LOG_FILE = path.join(__dirname, 'agentmail-log.json');

// ── Ensure log file exists ───────────────────────────────────
if (!fs.existsSync(LOG_FILE)) {
  fs.writeFileSync(LOG_FILE, JSON.stringify({ messages: [] }, null, 2));
}

// ── Append message to log ────────────────────────────────────
function appendMessage(entry) {
  try {
    const raw = fs.readFileSync(LOG_FILE, 'utf8');
    const log = JSON.parse(raw);
    log.messages.push(entry);
    // Keep last 1000 messages
    if (log.messages.length > 1000) {
      log.messages = log.messages.slice(-1000);
    }
    fs.writeFileSync(LOG_FILE, JSON.stringify(log, null, 2));
    return true;
  } catch (err) {
    console.error('[AgentMail] Failed to write log:', err.message);
    return false;
  }
}

// ── Validate payload ─────────────────────────────────────────
function validatePayload(body) {
  if (!body || typeof body !== 'object') return { valid: false, error: 'Invalid JSON body' };
  const { from, to, subject, body: msgBody } = body;
  if (!from) return { valid: false, error: 'Missing field: from' };
  if (!to) return { valid: false, error: 'Missing field: to' };
  if (!subject) return { valid: false, error: 'Missing field: subject' };
  if (!msgBody) return { valid: false, error: 'Missing field: body' };
  return { valid: true };
}

// ── HTTP Server ─────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const method = req.method;

  // CORS preflight
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // ── POST /webhook/agentmail ────────────────────────────────
  if (method === 'POST' && url.pathname === '/webhook/agentmail') {
    let rawBody = '';
    req.on('data', chunk => { rawBody += chunk; });
    req.on('end', () => {
      let parsed;
      try {
        parsed = JSON.parse(rawBody);
      } catch {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON body' }));
        return;
      }

      const validation = validatePayload(parsed);
      if (!validation.valid) {
        console.log(`[AgentMail] ❌ Validation failed: ${validation.error}`);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: validation.error }));
        return;
      }

      const entry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        timestamp: new Date().toISOString(),
        from: parsed.from,
        to: parsed.to,
        subject: parsed.subject,
        body: parsed.body,
        metadata: parsed.metadata || {},
      };

      // Log to console
      console.log('');
      console.log('╔══════════════════════════════════════════╗');
      console.log('║  🤖 AgentMail Received                   ║');
      console.log('╠══════════════════════════════════════════╣');
      console.log(`║  From:    ${entry.from}`);
      console.log(`║  To:      ${entry.to}`);
      console.log(`║  Subject: ${entry.subject}`);
      console.log(`║  Time:    ${entry.timestamp}`);
      console.log(`║  ID:      ${entry.id}`);
      console.log('╠══════════════════════════════════════════╣');
      console.log(`║  Body: ${entry.body.slice(0, 80)}${entry.body.length > 80 ? '...' : ''}`);
      console.log('╚══════════════════════════════════════════╝');
      console.log('');

      // Write to file
      const saved = appendMessage(entry);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'received',
        id: entry.id,
        saved,
        message: 'AgentMail logged successfully'
      }));
    });

    req.on('error', err => {
      console.error('[AgentMail] Request error:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    });
    return;
  }

  // ── GET /webhook/agentmail ────────────────────────────────
  if (method === 'GET' && url.pathname === '/webhook/agentmail') {
    try {
      const raw = fs.readFileSync(LOG_FILE, 'utf8');
      const log = JSON.parse(raw);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(log, null, 2));
    } catch {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ messages: [] }));
    }
    return;
  }

  // ── Health check ──────────────────────────────────────────
  if (method === 'GET' && url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'AgentMail Webhook', uptime: process.uptime() }));
    return;
  }

  // ── 404 ──────────────────────────────────────────────────
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`🤖 AgentMail Webhook Server`);
  console.log(`   Listening on http://localhost:${PORT}`);
  console.log(`   POST  /webhook/agentmail  — receive mail`);
  console.log(`   GET   /webhook/agentmail  — view log`);
  console.log(`   GET   /health             — health check`);
  console.log(`   Log file: ${LOG_FILE}`);
});

process.on('SIGTERM', () => {
  console.log('\n[AgentMail] Shutting down...');
  server.close(() => process.exit(0));
});
