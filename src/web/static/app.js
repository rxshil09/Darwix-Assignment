// ApexCare Voice Agent & Knowledge Base Console JavaScript

let sessionId = null;
let isCallActive = false;
let isMuted = false;
let callStartTime = null;
let timerInterval = null;
let recognition = null;
let isListening = false;

// DOM Elements
const btnStartCall = document.getElementById("btn-start-call");
const btnMute = document.getElementById("btn-mute");
const btnEscalate = document.getElementById("btn-escalate");
const btnSend = document.getElementById("btn-send");
const inputText = document.getElementById("user-input-text");
const speechForm = document.getElementById("speech-form");
const callTimer = document.getElementById("call-timer");
const statusLabel = document.getElementById("call-status-label");
const transcriptFeed = document.getElementById("transcript-feed");
const citationsFeed = document.getElementById("citations-feed");
const agentAvatar = document.getElementById("agent-avatar");
const audioPlayer = document.getElementById("tts-audio-player");
const canvas = document.getElementById("waveform");
const canvasCtx = canvas.getContext("2d");

// CRM elements
const crmBadge = document.getElementById("crm-status-badge");
const crmLeadId = document.getElementById("crm-lead-id");
const crmCallerName = document.getElementById("crm-caller-name");
const crmAge = document.getElementById("crm-age");
const crmPec = document.getElementById("crm-pec");
const crmTier = document.getElementById("crm-tier");
const crmPremium = document.getElementById("crm-premium");

// Setup Tabs
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    const targetId = btn.getAttribute("data-tab");
    document.getElementById(targetId).classList.add("active");
  });
});

// Setup Demo Quick Chips
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    const msg = chip.getAttribute("data-msg");
    if (!isCallActive) {
      startCall().then(() => {
        setTimeout(() => sendUserMessage(msg), 1500);
      });
    } else {
      sendUserMessage(msg);
    }
  });
});

// Initialize Speech Recognition
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("SpeechRecognition not supported in this browser; falling back to manual input.");
    return null;
  }
  const recog = new SpeechRecognition();
  recog.continuous = false;
  recog.interimResults = false;
  recog.lang = "en-US";

  recog.onresult = (event) => {
    const text = event.results[0][0].transcript;
    if (text) {
      sendUserMessage(text);
    }
  };

  recog.onerror = (err) => {
    console.warn("SpeechRecognition error:", err);
    isListening = false;
    statusLabel.textContent = "Mic idle (type or click test buttons)";
  };

  recog.onend = () => {
    isListening = false;
    if (isCallActive && !isMuted) {
      // Prompt user or wait
    }
  };

  return recog;
}

recognition = initSpeechRecognition();

// Start / End Call
btnStartCall.addEventListener("click", () => {
  if (!isCallActive) {
    startCall();
  } else {
    endCall();
  }
});

async function startCall() {
  statusLabel.textContent = "Connecting to ApexCare Advisor...";
  btnStartCall.disabled = true;

  try {
    const res = await fetch("/api/call/start", { method: "POST" });
    const data = await res.json();
    sessionId = data.session_id;
    isCallActive = true;

    btnStartCall.disabled = false;
    btnStartCall.innerHTML = '<span class="btn-icon">🛑</span> End Voice Call';
    btnStartCall.classList.add("btn-end");
    btnMute.disabled = false;
    btnEscalate.disabled = false;
    btnSend.disabled = false;

    // Start timer
    callStartTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);

    // Append greeting to transcript
    appendAssistantBubble(data.greeting, []);
    statusLabel.textContent = "Sarah is speaking...";
    playAudio(data.audio_url);

  } catch (err) {
    console.error("Start call error:", err);
    statusLabel.textContent = "Connection failed. Please retry.";
    btnStartCall.disabled = false;
  }
}

function endCall() {
  isCallActive = false;
  clearInterval(timerInterval);
  timerInterval = null;
  btnStartCall.innerHTML = '<span class="btn-icon">📞</span> Start Voice Call';
  btnStartCall.classList.remove("btn-end");
  btnMute.disabled = true;
  btnEscalate.disabled = true;
  btnSend.disabled = true;
  statusLabel.textContent = "Call disconnected.";
  agentAvatar.classList.remove("speaking");
  if (recognition) recognition.stop();
  audioPlayer.pause();
}

function updateTimer() {
  const elapsedSec = Math.floor((Date.now() - callStartTime) / 1000);
  const mins = String(Math.floor(elapsedSec / 60)).padStart(2, "0");
  const secs = String(elapsedSec % 60).padStart(2, "0");
  callTimer.textContent = `${mins}:${secs}`;
}

// Send Message
speechForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = inputText.value.trim();
  if (text) {
    sendUserMessage(text);
    inputText.value = "";
  }
});

async function sendUserMessage(text) {
  if (!isCallActive) {
    alert("Please click 'Start Voice Call' first.");
    return;
  }

  appendUserBubble(text);
  statusLabel.textContent = "Sarah is thinking (grounding from KB)...";

  try {
    const res = await fetch("/api/call/turn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        user_transcript: text
      })
    });

    const data = await res.json();
    appendAssistantBubble(data.reply, data.citations);

    // Update citations HUD
    if (data.citations && data.citations.length > 0) {
      renderCitations(data.citations);
    }

    // Update CRM card
    if (data.session) {
      updateCRM(data.session, data.lead_quote);
    }

    // Speak reply
    statusLabel.textContent = "Sarah is speaking...";
    playAudio(data.audio_url);

  } catch (err) {
    console.error("Turn error:", err);
    statusLabel.textContent = "Error processing turn.";
  }
}

// Audio Playback & Visualizer
function playAudio(url) {
  if (!url) return;
  agentAvatar.classList.add("speaking");
  audioPlayer.src = url;
  audioPlayer.play().catch(e => console.warn("Autoplay blocked:", e));

  audioPlayer.onended = () => {
    agentAvatar.classList.remove("speaking");
    statusLabel.textContent = "Listening for your response...";
    if (recognition && !isMuted) {
      try {
        recognition.start();
        isListening = true;
      } catch (e) {}
    }
  };
}

// Waveform Animation (Canvas)
let phase = 0;
function drawWave() {
  requestAnimationFrame(drawWave);
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

  const isSpeaking = agentAvatar.classList.contains("speaking") || isListening;
  const amplitude = isSpeaking ? 18 : 3;

  canvasCtx.lineWidth = 2;
  canvasCtx.strokeStyle = isSpeaking ? "#00f2fe" : "rgba(255, 255, 255, 0.15)";
  canvasCtx.beginPath();

  const sliceWidth = canvas.width / 50;
  let x = 0;

  for (let i = 0; i < 50; i++) {
    const y = canvas.height / 2 + Math.sin(i * 0.2 + phase) * amplitude * Math.sin(i * 0.1);
    if (i === 0) canvasCtx.moveTo(x, y);
    else canvasCtx.lineTo(x, y);
    x += sliceWidth;
  }

  canvasCtx.stroke();
  phase += 0.08;
}
drawWave();

// Bubble Rendering
function appendUserBubble(text) {
  const div = document.createElement("div");
  div.className = "chat-bubble user";
  div.innerHTML = `<strong>You:</strong> ${text}`;
  transcriptFeed.appendChild(div);
  transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
}

function appendAssistantBubble(text, citations) {
  const div = document.createElement("div");
  div.className = "chat-bubble assistant";
  let html = `<strong>Sarah:</strong> ${text}`;

  if (citations && citations.length > 0) {
    html += '<div class="citation-pill-row">';
    citations.forEach(c => {
      html += `<span class="citation-badge" title="${c.title} (${c.source})">🔗 ${c.record_id} [${c.category}]</span>`;
    });
    html += '</div>';
  }

  div.innerHTML = html;
  transcriptFeed.appendChild(div);
  transcriptFeed.scrollTop = transcriptFeed.scrollHeight;
}

function renderCitations(citations) {
  citationsFeed.innerHTML = "";
  citations.forEach(c => {
    const card = document.createElement("div");
    card.className = "citation-card";
    card.innerHTML = `
      <div class="citation-card-header">
        <span class="rec-id">📌 ${c.record_id}</span>
        <span class="score">RRF: ${c.score}</span>
      </div>
      <div class="citation-title">${c.title}</div>
      <div class="citation-snippet">${c.snippet}</div>
      <div style="font-size:11px;color:#64748b;margin-top:4px;">Provenance: ${c.source}</div>
    `;
    citationsFeed.appendChild(card);
  });
}

function updateCRM(session, leadQuote) {
  if (session.caller_name) crmCallerName.textContent = session.caller_name;
  if (session.age) crmAge.textContent = `${session.age} years old`;
  if (session.pre_existing_conditions && session.pre_existing_conditions.length > 0) {
    crmPec.textContent = session.pre_existing_conditions.join(", ");
  }
  if (session.preferred_tier) crmTier.textContent = session.preferred_tier;

  if (session.qualification_status) {
    crmBadge.textContent = session.qualification_status;
    crmBadge.className = `badge ${session.qualification_status}`;
  }

  if (leadQuote) {
    crmLeadId.textContent = leadQuote.lead_id;
    crmPremium.textContent = `$${leadQuote.estimated_monthly_premium.toFixed(2)}/mo`;
  }
}

// Escalation button
btnEscalate.addEventListener("click", () => {
  sendUserMessage("I would like to speak to a human supervisor please.");
});
