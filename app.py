"""
MindBridge AI — Mental Health Awareness Chatbot
Powered by IBM Granite LLM via IBM WatsonX
Agentic AI with RAG pipeline, crisis detection, empathy engine, mindfulness agents

Project ID : 97e606c4-d17e-41dc-ab3e-68e2d396226d
Endpoint   : https://eu-de.ml.cloud.ibm.com
"""

import os
import json
import re
import random
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ═══════════════════════════════════════════════════════════════════════════════
# App Configuration
# ═══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = os.urandom(32)

# ─── IBM WatsonX Credentials ──────────────────────────────────────────────────
IBM_API_KEY    = "QZ5lgS18ri16jWwPZZrsA7_B0QeSfoIjRUDw84ToC6Kz"
IBM_PROJECT_ID = "97e606c4-d17e-41dc-ab3e-68e2d396226d"
IBM_URL        = "https://eu-de.ml.cloud.ibm.com"
GRANITE_MODEL  = "ibm/granite-13b-instruct-v2"

# ─── Knowledge Base Path ──────────────────────────────────────────────────────
KB_PATH = Path(__file__).parent / "knowledge_base" / "mental_health_kb.json"


# ═══════════════════════════════════════════════════════════════════════════════
# Load RAG Knowledge Base
# ═══════════════════════════════════════════════════════════════════════════════
def load_knowledge_base() -> dict:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

KB = load_knowledge_base()


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 1: Crisis Detection Agent
# Immediately intercepts crisis signals — bypasses LLM for user safety
# ═══════════════════════════════════════════════════════════════════════════════
CRISIS_KEYWORDS = [
    "suicidal", "suicide", "kill myself", "end my life", "don't want to live",
    "want to die", "no reason to live", "better off dead", "hurt myself",
    "self-harm", "cutting myself", "overdose on purpose", "end it all",
    "can't go on", "not worth living", "take my own life"
]

DISTRESS_KEYWORDS = [
    "hopeless", "worthless", "can't cope", "breaking down", "falling apart",
    "nobody cares", "no one cares", "completely alone", "give up", "no point",
    "so done", "done with everything", "exhausted with life"
]

def detect_crisis_level(text: str) -> str:
    """Returns 'crisis', 'distress', or 'normal'."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in CRISIS_KEYWORDS):
        return "crisis"
    if any(kw in text_lower for kw in DISTRESS_KEYWORDS):
        return "distress"
    return "normal"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 2: RAG Retrieval Agent
# Retrieves relevant trusted knowledge before calling the LLM
# ═══════════════════════════════════════════════════════════════════════════════
def retrieve_context(query: str) -> list:
    """Keyword-semantic matching over the curated knowledge base topics."""
    query_lower = query.lower()
    matched = []
    for topic in KB["topics"]:
        score = sum(1 for kw in topic.get("keywords", []) if kw in query_lower)
        if score > 0:
            matched.append((score, topic))
    matched.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in matched[:3]]   # top-3 most relevant


def format_rag_context(topics: list) -> str:
    """Format retrieved topics into a concise context block for the prompt."""
    if not topics:
        return ""
    parts = []
    for t in topics:
        content = t.get("content", "")[:600]
        tips    = t.get("tips", [])[:3]
        tips_text = "\n".join(f"  • {tip}" for tip in tips)
        parts.append(
            f"[Knowledge: {t['title']}]\n{content}\n"
            + (f"Evidence-based tips:\n{tips_text}" if tips else "")
        )
    return "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 3: Empathy Classification Agent
# Detects emotional state to calibrate response tone
# ═══════════════════════════════════════════════════════════════════════════════
EMOTIONAL_INDICATORS = {
    "grief":       ["grief", "loss", "died", "death", "mourning", "passed away", "bereavement"],
    "anger":       ["angry", "furious", "rage", "frustrated", "mad", "irritated"],
    "fear":        ["scared", "terrified", "afraid", "frightened", "phobia"],
    "shame":       ["ashamed", "embarrassed", "humiliated", "guilty", "shame"],
    "loneliness":  ["lonely", "alone", "isolated", "no friends", "no one"],
    "joy_seeking": ["happy", "better", "improve", "grow", "positive", "hopeful"],
}

def classify_emotion(text: str) -> str:
    text_lower = text.lower()
    for emotion, indicators in EMOTIONAL_INDICATORS.items():
        if any(ind in text_lower for ind in indicators):
            return emotion
    return "general"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent 4: Intent Router Agent
# Routes each query to the correct handler or prompt strategy
# ═══════════════════════════════════════════════════════════════════════════════
def classify_intent(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["breathe", "breathing exercise", "calm me", "panic", "ground me", "grounding"]):
        return "exercise"
    if any(w in text_lower for w in ["meditate", "meditation", "mindful", "mindfulness"]):
        return "mindfulness"
    if any(w in text_lower for w in ["tip", "advice", "help me", "what should", "how do i", "how can i"]):
        return "advice"
    if any(w in text_lower for w in ["helpline", "hotline", "emergency", "call", "crisis number", "number to call"]):
        return "helpline"
    if any(w in text_lower for w in ["affirmation", "motivat", "positive", "inspire", "encourage"]):
        return "affirmation"
    return "conversation"


# ═══════════════════════════════════════════════════════════════════════════════
# IBM Granite Model Initialization
# ═══════════════════════════════════════════════════════════════════════════════
def get_granite_model() -> ModelInference:
    credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
    params = {
        GenParams.MAX_NEW_TOKENS:     900,
        GenParams.MIN_NEW_TOKENS:     40,
        GenParams.TEMPERATURE:        0.65,
        GenParams.TOP_P:              0.92,
        GenParams.REPETITION_PENALTY: 1.15,
    }
    return ModelInference(
        model_id=GRANITE_MODEL,
        credentials=credentials,
        project_id=IBM_PROJECT_ID,
        params=params
    )


# ═══════════════════════════════════════════════════════════════════════════════
# System Persona & Prompt Builders
# ═══════════════════════════════════════════════════════════════════════════════
SYSTEM_PERSONA = """You are MindBridge, a compassionate, trauma-informed AI mental health awareness assistant powered by IBM Granite.

Your core principles:
1. EMPATHY FIRST — Always validate the user's feelings before offering information or advice.
2. NON-JUDGMENTAL — Accept all feelings without judgment or criticism.
3. SAFETY — Never provide advice that could cause harm. Always recommend professional help for serious issues.
4. EVIDENCE-BASED — Ground all guidance in recognized psychological research and clinical evidence.
5. BOUNDARIES — Clearly remind users you are an AI, not a therapist or medical professional.
6. CULTURAL SENSITIVITY — Respect diverse cultural perspectives on mental health.
7. EMPOWERMENT — Help users build their own coping skills and self-awareness.

Communication style: Warm, gentle, and supportive. Use empathetic language.
Keep responses concise but thorough (3-5 paragraphs max). End with a gentle follow-up question."""


def build_main_prompt(user_message: str, rag_context: str, emotion: str,
                      intent: str, conversation_history: list, crisis_level: str) -> str:
    history_text = ""
    if conversation_history:
        recent = conversation_history[-6:]
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'MindBridge'}: {m['content']}"
            for m in recent
        )

    crisis_instruction = ""
    if crisis_level == "crisis":
        crisis_instruction = (
            "\n*** CRITICAL: User may be in crisis. Lead with immediate compassion. "
            "Ask if they are safe. Gently provide crisis helpline numbers. "
            "Do NOT dismiss or minimize their pain. ***"
        )
    elif crisis_level == "distress":
        crisis_instruction = (
            "\n*** NOTE: User shows significant distress. Lead with validation and warmth. "
            "Gently offer professional resources. ***"
        )

    emotion_instruction = {
        "grief":       "User is grieving. Acknowledge their loss with deep compassion first.",
        "anger":       "User is angry. Validate the anger — it is a valid emotion. Help them feel heard.",
        "fear":        "User is experiencing fear. Create safety first. Reassure them.",
        "shame":       "User experiences shame. Counter with unconditional acceptance.",
        "loneliness":  "User feels lonely. Acknowledge the pain and affirm their worth.",
        "joy_seeking": "User seeks growth. Encourage and support their positive momentum.",
        "general":     ""
    }.get(emotion, "")

    return f"""{SYSTEM_PERSONA}
{crisis_instruction}
{emotion_instruction}

--- Evidence-Based Context (from trusted mental health resources) ---
{rag_context if rag_context else "Provide general compassionate support."}
--- End Context ---

Conversation History:
{history_text if history_text else "This is the start of the conversation."}

User: {user_message}
Intent: {intent}

MindBridge response (warm, empathetic, evidence-based):"""


def build_exercise_prompt(exercise_type: str) -> str:
    return f"""{SYSTEM_PERSONA}

The user wants a guided {exercise_type} exercise right now.
Provide numbered, step-by-step guidance with timing/counts. Use a calm, encouraging voice.
Keep it doable in 3-5 minutes. End with a gentle affirmation.

Guided {exercise_type}:"""


# ═══════════════════════════════════════════════════════════════════════════════
# Output Sanitizer
# ═══════════════════════════════════════════════════════════════════════════════
def sanitize(text: str) -> str:
    text = re.sub(r"<\|.*?\|>|\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", "", text)
    return text.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Pre-built Crisis Response (safe, immediate — no LLM latency)
# ═══════════════════════════════════════════════════════════════════════════════
CRISIS_RESPONSE = """I hear you, and I am truly glad you reached out right now. What you are feeling matters deeply, and you do not have to face this alone.

Your safety is the most important thing right now. **Please reach out to a crisis helpline immediately** — they are free, confidential, and available 24/7:

**Immediate Help:**
- **USA:** Call or text **988** (Suicide & Crisis Lifeline)
- **UK:** Call **116 123** (Samaritans — free, 24/7)
- **India:** Call **9152987821** (iCall) or **1860-2662-345**
- **Canada:** Call **1-833-456-4566** (Crisis Services Canada)
- **Australia:** Call **13 11 14** (Lifeline)
- **Worldwide:** Text **HOME** to **741741** (Crisis Text Line)
- **All countries:** https://www.iasp.info/resources/Crisis_Centres/

The pain you are feeling right now is real, and it is temporary. Crises pass with the right support. You deserve care.

If you are in immediate danger, please call your local emergency services (911, 999, 112).

I am here with you. Can you tell me more about what is happening right now?"""


# ═══════════════════════════════════════════════════════════════════════════════
# DISCLAIMER
# ═══════════════════════════════════════════════════════════════════════════════
DISCLAIMER = (
    "\n\n---\n"
    "*Privacy: This conversation is session-only and not stored or shared. "
    "Disclaimer: MindBridge is an AI for mental health awareness and education only — "
    "not a substitute for professional mental health care. "
    "If you are struggling, please consult a licensed therapist or counselor.*"
)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()[:1000]

    if "history" not in session:
        session["history"] = []

    # Agent 1: Crisis Detection
    crisis_level = detect_crisis_level(user_message)
    if crisis_level == "crisis":
        session["history"].append({"role": "user",      "content": user_message})
        session["history"].append({"role": "assistant", "content": CRISIS_RESPONSE})
        session.modified = True
        return jsonify({
            "reply":          CRISIS_RESPONSE,
            "crisis_level":   "crisis",
            "show_helplines": True,
            "status":         "success"
        })

    # Agent 2: RAG Retrieval
    retrieved_topics = retrieve_context(user_message)
    rag_context      = format_rag_context(retrieved_topics)

    # Agent 3: Emotion Classification
    emotion = classify_emotion(user_message)

    # Agent 4: Intent Routing
    intent = classify_intent(user_message)

    # Direct helpline response
    if intent == "helpline":
        helplines = KB.get("global_helplines", [])
        response  = "Here are verified crisis helplines available globally:\n\n"
        for hl in helplines:
            response += f"**{hl['country']}** — {hl['name']}: `{hl['contact']}`\n"
        response += "\nAll helplines are free and confidential. You deserve support. 💙"
        return jsonify({"reply": response, "status": "success", "intent": "helpline"})

    # Direct affirmation response
    if intent == "affirmation":
        aff   = random.choice(KB.get("affirmations", ["You are enough."]))
        reply = (
            f"💙 Here is something I would like you to sit with:\n\n"
            f"*\"{aff}\"*\n\n"
            f"Take a slow, deep breath as you let those words settle in. "
            f"You are seen, heard, and valued. Would you like to talk about what is on your mind?"
        )
        return jsonify({"reply": reply, "status": "success", "intent": "affirmation"})

    # IBM Granite LLM call
    try:
        model = get_granite_model()

        if intent in ("exercise", "mindfulness"):
            label  = "breathing and grounding" if intent == "exercise" else "mindfulness meditation"
            prompt = build_exercise_prompt(label)
        else:
            prompt = build_main_prompt(
                user_message=user_message,
                rag_context=rag_context,
                emotion=emotion,
                intent=intent,
                conversation_history=session["history"],
                crisis_level=crisis_level
            )

        raw_reply = model.generate_text(prompt=prompt)
        reply     = sanitize(raw_reply)

        if intent in ("advice", "conversation") and retrieved_topics:
            reply += DISCLAIMER

        session["history"].append({"role": "user",      "content": user_message})
        session["history"].append({"role": "assistant", "content": reply})
        session["history"] = session["history"][-20:]
        session.modified   = True

        return jsonify({
            "reply":        reply,
            "crisis_level": crisis_level,
            "emotion":      emotion,
            "intent":       intent,
            "topics_found": [t["title"] for t in retrieved_topics],
            "status":       "success"
        })

    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


@app.route("/api/breathing-exercise", methods=["GET"])
def breathing_exercise():
    topic = next((t for t in KB["topics"] if t["id"] == "breathing_exercises"), None)
    if topic:
        return jsonify({"exercises": topic.get("exercises", []), "status": "success"})
    return jsonify({"exercises": [], "status": "not_found"})


@app.route("/api/helplines", methods=["GET"])
def helplines():
    return jsonify({"helplines": KB.get("global_helplines", []), "status": "success"})


@app.route("/api/affirmation", methods=["GET"])
def affirmation():
    return jsonify({
        "affirmation": random.choice(KB.get("affirmations", ["You are enough."])),
        "status": "success"
    })


@app.route("/api/topics", methods=["GET"])
def topics():
    topic_list = [
        {"id": t["id"], "title": t["title"]}
        for t in KB["topics"] if t["id"] != "crisis"
    ]
    return jsonify({"topics": topic_list, "status": "success"})


@app.route("/api/topic/<topic_id>", methods=["GET"])
def get_topic(topic_id: str):
    topic = next((t for t in KB["topics"] if t["id"] == topic_id), None)
    if topic:
        return jsonify({
            "title":   topic["title"],
            "content": topic.get("content", ""),
            "tips":    topic.get("tips", []),
            "source":  topic.get("source", ""),
            "status":  "success"
        })
    return jsonify({"error": "Topic not found"}), 404


@app.route("/api/clear-session", methods=["POST"])
def clear_session():
    session.clear()
    return jsonify({"status": "cleared", "message": "Conversation history cleared."})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status":  "ok",
        "model":   GRANITE_MODEL,
        "service": "MindBridge AI — Mental Health Awareness Chatbot",
        "version": "1.0.0"
    })


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
