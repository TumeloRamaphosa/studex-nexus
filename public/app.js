const API = '';

function clearEl(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

function emptyNote(el, text) {
  clearEl(el);
  const p = document.createElement('p');
  p.style.color = 'var(--text-secondary)';
  p.style.fontSize = '0.9rem';
  p.textContent = text;
  el.appendChild(p);
}

function buildPostItem(post, type) {
  const item = document.createElement('div');
  item.className = `post-item${type ? ` ${type}` : ''}`;
  if (post.id) item.dataset.id = post.id;

  const platform = document.createElement('div');
  platform.className = 'post-platform';
  platform.textContent = post.platform || 'Social';

  const caption = document.createElement('div');
  caption.className = 'post-caption';
  caption.textContent = post.caption || post.text || '';

  const time = document.createElement('div');
  time.className = 'post-time';
  time.textContent = post.timeLabel || post.createdAt || post.postTime || '';

  item.append(platform, caption, time);

  if (post.mediaUrls?.length) {
    const img = document.createElement('img');
    img.className = 'post-image';
    img.src = post.mediaUrls[0];
    img.alt = '';
    item.appendChild(img);
  }

  return item;
}

function renderPosts(container, posts, type, emptyText) {
  clearEl(container);
  if (!posts?.length) {
    emptyNote(container, emptyText);
    return;
  }
  posts.forEach((post) => container.appendChild(buildPostItem(post, type)));
}

function strong(text) {
  const el = document.createElement('strong');
  el.textContent = text;
  return el;
}

function buildRecommendationCard(rec) {
  const card = document.createElement('div');
  card.className = 'recommendation-card';
  card.dataset.recId = rec.id;

  const content = document.createElement('div');
  content.className = 'rec-content';

  const topic = document.createElement('div');
  topic.className = 'rec-topic';
  topic.textContent = rec.topic;

  const caption = document.createElement('div');
  caption.className = 'rec-caption';
  caption.textContent = `"${rec.caption}"`;

  const meta = document.createElement('div');
  meta.className = 'rec-meta';

  const platformItem = document.createElement('div');
  platformItem.className = 'rec-meta-item';
  platformItem.append('Platform: ', strong(rec.platform));

  const scoreItem = document.createElement('div');
  scoreItem.className = 'rec-meta-item';
  scoreItem.append('Timing Score: ', strong(`${rec.timingScore}%`));

  const timing = document.createElement('div');
  timing.className = 'rec-timing';
  const bar = document.createElement('div');
  bar.className = 'timing-bar';
  const fill = document.createElement('div');
  fill.className = 'timing-fill';
  fill.style.width = `${rec.timingScore}%`;
  bar.appendChild(fill);
  timing.appendChild(bar);

  const windowItem = document.createElement('div');
  windowItem.className = 'rec-meta-item';
  windowItem.append('Best Window: ', strong(rec.bestWindow));

  meta.append(platformItem, scoreItem, timing, windowItem);
  content.append(topic, caption, meta);

  const actions = document.createElement('div');
  actions.className = 'rec-actions';

  const approve = document.createElement('button');
  approve.className = 'btn btn-approve';
  approve.textContent = 'Approve';
  approve.addEventListener('click', () => handleRecAction(rec.id, 'approve'));

  const reject = document.createElement('button');
  reject.className = 'btn btn-reject';
  reject.textContent = 'Reject';
  reject.addEventListener('click', () => handleRecAction(rec.id, 'reject'));

  actions.append(approve, reject);
  card.append(content, actions);
  return card;
}

function renderRecommendations(items) {
  const list = document.getElementById('recommendationsList');
  clearEl(list);
  if (!items?.length) {
    const p = document.createElement('p');
    p.style.color = 'var(--text-secondary)';
    p.style.fontFamily = 'Space Mono, monospace';
    p.style.fontSize = '0.75rem';
    p.textContent = 'No recommendations yet. Click Generate below.';
    list.appendChild(p);
    return;
  }
  items.forEach((rec) => list.appendChild(buildRecommendationCard(rec)));
}

function buildWorkflowCard(w) {
  const card = document.createElement('div');
  card.className = 'workflow-card';
  const info = document.createElement('div');
  info.className = 'workflow-info';
  const title = document.createElement('h4');
  title.textContent = w.name;
  const schedule = document.createElement('div');
  schedule.className = 'workflow-schedule';
  schedule.textContent = w.schedule;
  info.append(title, schedule);
  const dot = document.createElement('div');
  dot.className = `status-dot ${w.status}`;
  card.append(info, dot);
  return card;
}

const CONNECTOR_LABELS = {
  ollama: 'Ollama Cloud',
  blotato: 'Blotato',
  feedhive: 'FeedHive',
  freepik: 'Freepik',
  higgsfield: 'Higgsfield',
  notion: 'Notion',
  orgo: 'Orgo',
};

function connectorDetailText(key, c) {
  if (c.connected) {
    if (key === 'ollama') return `${c.models} models`;
    if (key === 'blotato') return `${c.accounts} accounts`;
    if (key === 'higgsfield') return c.detail;
    if (key === 'freepik') return `${c.sampleResults} sample results`;
    if (key === 'notion') return `${c.pages ?? 0} cards`;
    return 'OK';
  }
  return c.error || 'Disconnected';
}

function buildConnectorCard(key, c) {
  const card = document.createElement('div');
  card.className = 'workflow-card';
  const info = document.createElement('div');
  info.className = 'workflow-info';
  const title = document.createElement('h4');
  title.textContent = CONNECTOR_LABELS[key] || key;
  const detail = document.createElement('div');
  detail.className = `connector-detail${c.connected ? '' : ' error'}`;
  detail.textContent = connectorDetailText(key, c);
  info.append(title, detail);
  const dot = document.createElement('div');
  dot.className = `status-dot ${c.connected ? 'green' : 'red'}`;
  card.append(info, dot);
  return card;
}

function renderCredentials(rows) {
  const grid = document.getElementById('credentialGrid');
  if (!grid) return;
  clearEl(grid);
  if (!rows?.length) {
    emptyNote(grid, 'No credential probes yet');
    return;
  }
  rows.forEach((row) => {
    const card = document.createElement('div');
    card.className = 'workflow-card';
    const info = document.createElement('div');
    info.className = 'workflow-info';
    const title = document.createElement('h4');
    title.textContent = row.name;
    const detail = document.createElement('div');
    const active = row.status === 'active';
    detail.className = `connector-detail${active ? '' : ' error'}`;
    detail.textContent = active ? `ACTIVE · ${row.evidence}` : `UNKNOWN · ${row.evidence}`;
    info.append(title, detail);
    const dot = document.createElement('div');
    dot.className = `status-dot ${active ? 'green' : 'amber'}`;
    card.append(info, dot);
    grid.appendChild(card);
  });
}

function renderConnectors(connectors) {
  const grid = document.getElementById('connectorGrid');
  if (!grid || !connectors) return;
  clearEl(grid);
  Object.entries(connectors).forEach(([key, c]) => grid.appendChild(buildConnectorCard(key, c)));
}

async function loadDashboard() {
  const indicator = document.getElementById('refreshIndicator');
  indicator.classList.add('active');
  try {
    const [dash, status] = await Promise.all([
      fetch(`${API}/api/dashboard`).then((r) => r.json()),
      fetch(`${API}/api/status`).then((r) => r.json()),
    ]);
    if (dash.error) throw new Error(dash.error);

    renderPosts(document.getElementById('scheduledPosts'), dash.scheduled, '', 'No scheduled posts');
    renderPosts(document.getElementById('pendingPosts'), dash.pending, 'pending', 'Queue empty');
    renderPosts(document.getElementById('postedPosts'), dash.postedToday, 'approved', 'Nothing posted today yet');
    renderRecommendations(dash.recommendations || []);

    const scheduledCount = document.getElementById('scheduledCount');
    const pendingCount = document.getElementById('pendingCount');
    const postedCount = document.getElementById('postedCount');
    if (scheduledCount) scheduledCount.textContent = `${dash.counts?.scheduled || 0} Posts`;
    if (pendingCount) pendingCount.textContent = `${dash.counts?.pending || 0} Pending`;
    if (postedCount) postedCount.textContent = `${dash.counts?.postedToday || 0} Complete`;
    const statPosts = document.getElementById('statPosts');
    if (statPosts) statPosts.textContent = String(dash.counts?.postedToday ?? '—');

    document.getElementById('pendingReview').textContent = dash.counts?.recommendations || 0;
    document.getElementById('recsToday').textContent = dash.counts?.recommendations || 0;
    document.getElementById('approvedToday').textContent = dash.counts?.postedToday || 0;
    document.getElementById('lastRun').textContent = status.lastRun || '—';

    renderConnectors(status.connectors);
    renderCredentials(status.credentials);

    const wfGrid = document.getElementById('workflowGrid');
    if (wfGrid && status.workflows) {
      clearEl(wfGrid);
      status.workflows.forEach((w) => wfGrid.appendChild(buildWorkflowCard(w)));
    }
  } catch (err) {
    console.error('Dashboard load failed:', err);
  } finally {
    indicator.classList.remove('active');
  }
}

async function generateRecommendations() {
  const btn = document.getElementById('generateBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Generating…'; }
  try {
    await fetch(`${API}/api/generate/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count: 3 }),
    });
    await loadDashboard();
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Generate Recommendations'; }
  }
}

function refreshData() { loadDashboard(); }

async function askBrain() {
  const role = document.getElementById('brainRole').value;
  const question = document.getElementById('brainQuestion').value.trim();
  const btn = document.getElementById('brainAskBtn');
  const resultEl = document.getElementById('brainResult');
  const errorEl = document.getElementById('brainError');
  const answerEl = document.getElementById('brainAnswer');
  const noteEl = document.getElementById('brainNotePath');

  errorEl.style.display = 'none';
  resultEl.style.display = 'none';
  if (!question) {
    errorEl.textContent = 'Enter a question first.';
    errorEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Asking…';
  try {
    const res = await fetch(`${API}/api/brain/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, question }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Ask Brain failed');
    answerEl.textContent = data.answer;
    noteEl.textContent = `Saved to ${data.notePath}`;
    resultEl.style.display = 'block';
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Ask';
  }
}

async function handleRecAction(recId, action) {
  const card = document.querySelector(`[data-rec-id="${recId}"]`);
  if (!card) return;
  card.style.opacity = '0.5';
  card.style.pointerEvents = 'none';
  try {
    await fetch(`${API}/api/recommendations/${recId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action }),
    });
    card.style.transition = 'all 0.5s ease';
    card.style.transform = 'translateX(100px)';
    card.style.opacity = '0';
    setTimeout(() => { card.remove(); loadDashboard(); }, 400);
  } catch (err) {
    console.error(err);
    card.style.opacity = '1';
    card.style.pointerEvents = '';
  }
}

async function checkPortalLogin() {
  const password = document.getElementById('portalPassword').value;
  const loginForm = document.getElementById('loginForm');
  const portalContent = document.getElementById('portalContent');
  const loginError = document.getElementById('loginError');
  try {
    const res = await fetch(`${API}/api/portal/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });
    if (res.ok) {
      loginForm.style.display = 'none';
      portalContent.classList.add('active');
      loginError.style.display = 'none';
    } else {
      loginError.style.display = 'block';
      document.getElementById('portalPassword').value = '';
    }
  } catch {
    loginError.style.display = 'block';
  }
}

function logoutPortal() {
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('portalContent').classList.remove('active');
  document.getElementById('portalPassword').value = '';
}

function saveCaption(postId) {
  const captionEl = document.getElementById(`editCaption${postId}`);
  const btn = captionEl.nextElementSibling.nextElementSibling;
  const originalText = btn.textContent;
  btn.textContent = 'Saved!';
  btn.style.background = 'var(--green)';
  setTimeout(() => { btn.textContent = originalText; btn.style.background = ''; }, 1500);
}

function animateCounters() {
  document.querySelectorAll('[data-count]').forEach((counter) => {
    const target = parseFloat(counter.getAttribute('data-count'));
    const duration = 2000;
    const start = performance.now();
    function update(currentTime) {
      const progress = Math.min((currentTime - start) / duration, 1);
      const current = target * (1 - (1 - progress) ** 3);
      counter.textContent = target % 1 !== 0 ? current.toFixed(1) : Math.floor(current);
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  });
}

window.addEventListener('load', () => {
  setTimeout(animateCounters, 500);
  loadDashboard();
  setInterval(refreshData, 60000);
  document.getElementById('portalPassword').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') checkPortalLogin();
  });
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add('visible');
    }),
    { threshold: 0.1 },
  );
  document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));
});
