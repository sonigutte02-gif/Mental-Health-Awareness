/* ═══════════════════════════════════════════════════════════════════════════
   MindBridge AI — Frontend JavaScript
   Agentic AI client: empathetic chat, breathing engine, resources, helplines
   ═══════════════════════════════════════════════════════════════════════════ */
'use strict';

// ─── Tab Navigation ───────────────────────────────────────────────────────
function switchTab(btn, sectionId) {
  document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + sectionId).classList.add('active');
  if (btn) btn.classList.add('active');
  if (sectionId === 'resources')  loadResources();
  if (sectionId === 'helplines')  loadHelplines();
  if (sectionId === 'breathe')    loadExercises();
}

function closeBanner() {
  const b = document.getElementById('disclaimerBanner');
  if (b) b.style.display = 'none';
}

// ═══════════════════════════════════════════════════════════════════════════
// CHAT AGENT
// ═══════════════════════════════════════════════════════════════════════════
let isSending = false;

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function sendPrompt(btn) {
  document.getElementById('chatInput').value = btn.textContent.trim();
  document.getElementById('quickPrompts').style.display = 'none';
  sendMessage();
}

async function sendMessage() {
  if (isSending) return;
  const input   = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  isSending = true;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('sendBtn').disabled = true;
  document.getElementById('quickPrompts').style.display = 'none';

  appendMessage(message, 'user');
  const typingId = showTyping();

  try {
    const res  = await fetch('/api/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message })
    });
    const data = await res.json();

    removeTyping(typingId);

    if (data.error) {
      appendMessage('Sorry, I encountered an error: ' + data.error, 'bot', 'error');
      return;
    }

    const isCrisis = data.crisis_level === 'crisis';
    appendMessage(data.reply, 'bot', isCrisis ? 'crisis' : 'normal');

    if (data.topics_found && data.topics_found.length > 0) {
      appendTopicPills(data.topics_found);
    }
  } catch (err) {
    removeTyping(typingId);
    appendMessage('Network error. Please check your connection and try again.', 'bot', 'error');
  } finally {
    isSending = false;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
  }
}

function appendMessage(text, role, type) {
  type = type || 'normal';
  const win = document.getElementById('chatWindow');
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const msgDiv    = document.createElement('div');
  msgDiv.className = 'chat-msg ' + (role === 'user' ? 'user-msg' : 'bot-msg');
  if (type === 'crisis') msgDiv.classList.add('crisis-msg');

  const av = document.createElement('div');
  av.className   = 'msg-avatar';
  av.setAttribute('aria-hidden', 'true');
  av.textContent = role === 'user' ? '👤' : '🧠';

  const body   = document.createElement('div');
  body.className = 'msg-body';

  const bubble   = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = formatMessage(text);

  const time   = document.createElement('div');
  time.className   = 'msg-time';
  time.textContent = now;

  body.appendChild(bubble);
  body.appendChild(time);
  msgDiv.appendChild(av);
  msgDiv.appendChild(body);
  win.appendChild(msgDiv);
  win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
}

function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^#{1,3}\s(.+)$/gm, '<strong>$1</strong>')
    .replace(/^[-*]\s(.+)$/gm, '• $1')
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}

function appendTopicPills(topics) {
  const win = document.getElementById('chatWindow');
  const div = document.createElement('div');
  div.style.cssText = 'display:flex;gap:.4rem;flex-wrap:wrap;padding:0 .5rem;margin-top:-.5rem;';
  topics.forEach(function(t) {
    const pill = document.createElement('span');
    pill.style.cssText = 'background:#e8eefa;border:1px solid #c5d3f0;border-radius:999px;padding:.2rem .65rem;font-size:.7rem;color:#3d5fa5;';
    pill.textContent = '📚 ' + t;
    div.appendChild(pill);
  });
  win.appendChild(div);
  win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
}

function showTyping() {
  const win = document.getElementById('chatWindow');
  const id  = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.id        = id;
  div.className = 'chat-msg bot-msg';
  div.innerHTML = '<div class="msg-avatar" aria-hidden="true">🧠</div><div class="msg-body"><div class="typing-bubble"><span class="t-dot"></span><span class="t-dot"></span><span class="t-dot"></span></div></div>';
  win.appendChild(div);
  win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function clearConversation() {
  if (!confirm('Clear this conversation? This protects your privacy by removing session history.')) return;
  try { await fetch('/api/clear-session', { method: 'POST' }); } catch (_) {}
  const win = document.getElementById('chatWindow');
  win.innerHTML = '<div class="chat-msg bot-msg"><div class="msg-avatar" aria-hidden="true">🧠</div><div class="msg-body"><div class="msg-bubble"><p>Conversation cleared. Your privacy is protected. 🔒</p><p>I am here whenever you are ready to talk. What is on your mind?</p></div><div class="msg-time">Now</div></div></div>';
  document.getElementById('quickPrompts').style.display = 'flex';
}

// ═══════════════════════════════════════════════════════════════════════════
// AFFIRMATION
// ═══════════════════════════════════════════════════════════════════════════
async function loadAffirmation() {
  try {
    const data = await fetch('/api/affirmation').then(r => r.json());
    const el   = document.getElementById('affirmationText');
    if (el && data.affirmation) {
      el.style.opacity = '0';
      setTimeout(function() {
        el.textContent  = data.affirmation;
        el.style.transition = 'opacity .4s';
        el.style.opacity    = '1';
      }, 200);
    }
  } catch (_) {}
}

// ═══════════════════════════════════════════════════════════════════════════
// TOPICS SIDEBAR
// ═══════════════════════════════════════════════════════════════════════════
async function loadTopics() {
  try {
    const data = await fetch('/api/topics').then(r => r.json());
    const list = document.getElementById('topicsList');
    if (!list) return;
    list.innerHTML = '';
    (data.topics || []).forEach(function(t) {
      const btn      = document.createElement('button');
      btn.className  = 'topic-chip';
      btn.textContent = t.title;
      btn.onclick    = function() {
        document.getElementById('chatInput').value = 'Tell me about ' + t.title;
        switchTab(document.querySelector('[data-section="chat"]'), 'chat');
        sendMessage();
      };
      list.appendChild(btn);
    });
  } catch (_) {
    const list = document.getElementById('topicsList');
    if (list) list.innerHTML = '<span style="font-size:.78rem;color:#aaa">Could not load topics.</span>';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// BREATHING EXERCISE ENGINE
// ═══════════════════════════════════════════════════════════════════════════
var BREATHE_MODES = {
  box: {
    phases: [
      { label: 'Inhale', cls: 'inhale', duration: 4 },
      { label: 'Hold',   cls: 'hold',   duration: 4 },
      { label: 'Exhale', cls: 'exhale', duration: 4 },
      { label: 'Hold',   cls: 'hold2',  duration: 4 }
    ],
    tip: 'Box breathing is used by Navy SEALs and elite athletes to instantly calm the nervous system.'
  },
  '478': {
    phases: [
      { label: 'Inhale', cls: 'inhale', duration: 4 },
      { label: 'Hold',   cls: 'hold',   duration: 7 },
      { label: 'Exhale', cls: 'exhale', duration: 8 }
    ],
    tip: '4-7-8 breathing activates the parasympathetic nervous system, promoting deep relaxation and sleep.'
  },
  diaphragm: {
    phases: [
      { label: 'Breathe In',  cls: 'inhale', duration: 5 },
      { label: 'Breathe Out', cls: 'exhale', duration: 7 }
    ],
    tip: 'Diaphragmatic breathing engages the belly, maximizing oxygen exchange and reducing cortisol.'
  }
};

var breatheRunning   = false;
var breathePhaseIdx  = 0;
var breatheTimeout   = null;
var breatheCountdown = 0;
var breatheCountTimer = null;

function toggleBreath() {
  if (breatheRunning) { stopBreath(); } else { startBreath(); }
}
function startBreath() {
  breatheRunning = true;
  breathePhaseIdx = 0;
  document.getElementById('breatheStartBtn').textContent = '⏹ Stop';
  runBreathPhase();
}
function stopBreath() {
  breatheRunning = false;
  clearTimeout(breatheTimeout);
  clearInterval(breatheCountTimer);
  document.getElementById('breatheStartBtn').textContent = '▶ Start';
  document.getElementById('breatheInstruction').textContent = 'Paused';
  document.getElementById('breatheCount').textContent = '';
  document.getElementById('breatheCircle').className = 'breathe-circle';
}
function resetBreath() {
  stopBreath();
  var mode = document.getElementById('breatheMode').value;
  document.getElementById('breatheInstruction').textContent = 'Press Start';
  document.getElementById('breatheCount').textContent = '';
  document.getElementById('breatheTip').textContent = (BREATHE_MODES[mode] || BREATHE_MODES.box).tip;
}
function runBreathPhase() {
  if (!breatheRunning) return;
  var mode   = document.getElementById('breatheMode').value;
  var phases = (BREATHE_MODES[mode] || BREATHE_MODES.box).phases;
  var phase  = phases[breathePhaseIdx % phases.length];

  document.getElementById('breatheInstruction').textContent = phase.label;
  document.getElementById('breatheCircle').className = 'breathe-circle ' + phase.cls;
  breatheCountdown = phase.duration;
  document.getElementById('breatheCount').textContent = breatheCountdown;

  clearInterval(breatheCountTimer);
  breatheCountTimer = setInterval(function() {
    breatheCountdown--;
    if (breatheCountdown <= 0) { clearInterval(breatheCountTimer); }
    else { document.getElementById('breatheCount').textContent = breatheCountdown; }
  }, 1000);

  breatheTimeout = setTimeout(function() {
    breathePhaseIdx++;
    runBreathPhase();
  }, phase.duration * 1000);
}

var exercisesLoaded = false;
async function loadExercises() {
  if (exercisesLoaded) return;
  const grid = document.getElementById('exercisesGrid');
  if (!grid) return;
  try {
    const data = await fetch('/api/breathing-exercise').then(r => r.json());
    grid.innerHTML = '';
    (data.exercises || []).forEach(function(ex) {
      const card = document.createElement('div');
      card.className = 'exercise-card';
      const stepsHTML = ex.steps.map(function(s) { return '<li>' + s + '</li>'; }).join('');
      card.innerHTML = '<h4>' + ex.name + '</h4><div class="exercise-use">Best for: ' + ex.use_for + '</div><ol class="exercise-steps">' + stepsHTML + '</ol>';
      grid.appendChild(card);
    });
    exercisesLoaded = true;
  } catch (_) {
    grid.innerHTML = '<div class="loading-sm">Could not load exercises.</div>';
  }
}

function highlightStep(el) {
  document.querySelectorAll('.grounding-step').forEach(function(s) { s.classList.remove('active'); });
  el.classList.add('active');
}

// ═══════════════════════════════════════════════════════════════════════════
// RESOURCES TAB
// ═══════════════════════════════════════════════════════════════════════════
var resourcesLoaded = false;
async function loadResources() {
  if (resourcesLoaded) return;
  const grid = document.getElementById('resourcesGrid');
  if (!grid) return;
  const TOPIC_IDS = ['anxiety','depression','stress','mindfulness','sleep','self_care','relationships'];
  try {
    const results = await Promise.all(TOPIC_IDS.map(function(id) { return fetch('/api/topic/' + id).then(r => r.json()); }));
    grid.innerHTML = '';
    results.forEach(function(data) {
      if (data.error) return;
      const card = document.createElement('div');
      card.className = 'resource-card';
      const tipsHTML = (data.tips || []).slice(0, 3).map(function(t) { return '<li>' + t + '</li>'; }).join('');
      card.innerHTML = '<div class="resource-title">' + data.title + '</div><div class="resource-content">' + data.content.slice(0, 240) + '…</div>' + (tipsHTML ? '<ul class="resource-tips">' + tipsHTML + '</ul>' : '') + '<div class="resource-source">Source: ' + data.source + '</div>';
      grid.appendChild(card);
    });
    resourcesLoaded = true;
  } catch (_) {
    grid.innerHTML = '<div class="loading-sm">Could not load resources.</div>';
  }
}

function trackSelfCare() {
  var checked = document.querySelectorAll('.checklist-grid input:checked').length;
  var total   = document.querySelectorAll('.checklist-grid input').length;
  var score   = document.getElementById('selfcareScore');
  score.textContent   = checked + ' / ' + total + ' today';
  score.style.background = checked >= 7 ? '#dcfce7' : checked >= 4 ? '#e8f5ef' : '#f0f4f8';
  score.style.color      = checked >= 7 ? '#166534' : checked >= 4 ? '#4a7a5e' : '#5b7fcc';
}

// ═══════════════════════════════════════════════════════════════════════════
// HELPLINES TAB
// ═══════════════════════════════════════════════════════════════════════════
var helplinesLoaded = false;
async function loadHelplines() {
  if (helplinesLoaded) return;
  const grid = document.getElementById('helplinesGrid');
  if (!grid) return;
  try {
    const data = await fetch('/api/helplines').then(r => r.json());
    grid.innerHTML = '';
    (data.helplines || []).forEach(function(hl) {
      const card = document.createElement('div');
      card.className = 'helpline-card';
      card.innerHTML = '<div class="hl-country">' + hl.country + '</div><div class="hl-name">' + hl.name + '</div><div class="hl-contact">' + hl.contact + '</div>';
      grid.appendChild(card);
    });
    helplinesLoaded = true;
  } catch (_) {
    grid.innerHTML = '<div class="loading-sm">Could not load helplines.</div>';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', function() {
  loadAffirmation();
  loadTopics();
  var modeSelect = document.getElementById('breatheMode');
  if (modeSelect) modeSelect.addEventListener('change', resetBreath);
});
