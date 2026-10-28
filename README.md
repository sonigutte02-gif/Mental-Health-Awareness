# 🧠 MindBridge AI — Mental Health Awareness Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=flat-square&logo=flask)
![IBM WatsonX](https://img.shields.io/badge/IBM-WatsonX%20AI-0f62fe?style=flat-square&logo=ibm)
![IBM Granite](https://img.shields.io/badge/IBM-Granite%2013B-0f62fe?style=flat-square&logo=ibm)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**A compassionate Agentic AI-powered Mental Health Awareness Chatbot**  
*Powered by IBM Granite LLM · IBM WatsonX AI · IBM Bob*

[Features](#-features) · [Architecture](#-agentic-ai-architecture) · [Quick Start](#-quick-start) · [API](#-api-reference) · [Ethics](#-ai-ethics--safety) · [Helplines](#-crisis-helplines)

</div>

---

## 💙 Overview

MindBridge AI is a full-stack, web-based **Agentic AI mental health awareness application** built with IBM Granite. It provides empathetic conversations, mental health education, guided mindfulness exercises, self-care tools, and immediate crisis support — all grounded in a **RAG (Retrieval-Augmented Generation) pipeline** using trusted mental health knowledge from WHO, NIMH, APA, and SAMHSA.

> ⚠️ **This is an awareness and education tool only — not a replacement for professional mental health care.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Empathetic AI Chat** | IBM Granite-powered conversations with trauma-informed, non-judgmental responses |
| 🔍 **RAG Pipeline** | Retrieval-Augmented Generation from a curated mental health knowledge base (WHO, NIMH, APA) |
| 🆘 **Crisis Detection Agent** | Automatic detection of crisis language → immediate safe response + helplines (bypasses LLM) |
| 🧠 **Emotion Classification Agent** | Detects grief, anger, fear, shame, loneliness to calibrate empathy tone |
| 🎯 **Intent Router Agent** | Routes to exercise, mindfulness, helpline, affirmation, or conversation flows |
| 🌬️ **Breathing Exercises** | Animated interactive guides: Box (4-4-4-4), 4-7-8, Diaphragmatic |
| 🌿 **5-4-3-2-1 Grounding** | Interactive clickable anxiety grounding technique |
| 📚 **Mental Health Education** | 9 curated topics: anxiety, depression, stress, sleep, trauma, relationships, self-care |
| ✅ **Self-Care Checklist** | Daily trackable wellness habits with live scoring |
| 🆘 **Verified Helplines** | 15+ verified crisis helplines across 12+ countries |
| 🔒 **Privacy First** | Session-only conversations — nothing stored after session ends |
| ⚠️ **Ethical AI** | IBM ethical AI principles enforced (HAM tone, guardrails, disclaimers) |

---

## 🏗️ Project Structure

```
mindbridge_ai/
├── app.py                          # Flask backend — 4 AI agents + IBM Granite
├── requirements.txt                # Python dependencies
├── run.bat                         # Windows one-click launcher
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── knowledge_base/
│   └── mental_health_kb.json       # Curated RAG knowledge base (WHO/NIMH/APA)
├── templates/
│   └── index.html                  # 4-tab responsive SPA frontend
└── static/
    ├── css/
    │   └── style.css               # Calming, accessible design system
    └── js/
        └── app.js                  # Agentic AI frontend client
```

---

## 🤖 Agentic AI Architecture

```
User Message
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│  Agent 1: Crisis Detection Agent                           │
│  Keyword safety gate — bypasses LLM entirely for crisis    │
│  Crisis → Immediate safe response + 15 verified helplines  │
└──────────────────────────┬─────────────────────────────────┘
                           │ Safe query
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Agent 2: RAG Retrieval Agent                              │
│  Semantic keyword search over curated KB                   │
│  Returns top-3 most relevant topics (WHO, NIMH, APA)       │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Agent 3: Emotion Classification Agent                     │
│  Detects: grief / anger / fear / shame / loneliness        │
│  Calibrates empathy tone in the LLM prompt                 │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Agent 4: Intent Router Agent                              │
│  Routes to: exercise / mindfulness / helpline /            │
│             affirmation / advice / conversation            │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
               ┌───────────────────────┐
               │  IBM Granite 13B LLM  │
               │  (IBM WatsonX AI)     │
               │  Trauma-informed      │
               │  empathetic response  │
               └───────────┬───────────┘
                           ▼
             Sanitized + Disclaimed Response → User
```

---

## ⚙️ Prerequisites

- **Python** 3.9 or higher
- **pip** package manager
- IBM WatsonX account with access to Granite models
- Internet connection (to call IBM WatsonX API)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sonigutte02-gif/Mental-Health-Awareness.git
cd Mental-Health-Awareness
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure IBM WatsonX Credentials

The credentials are pre-configured in `app.py`. To update them:

```python
IBM_API_KEY    = "your-ibm-api-key"
IBM_PROJECT_ID = "your-project-id"
IBM_URL        = "https://eu-de.ml.cloud.ibm.com"
GRANITE_MODEL  = "ibm/granite-13b-instruct-v2"
```

> 💡 **Production tip:** Use environment variables or a `.env` file with `python-dotenv` instead of hardcoding credentials.

### 5. Run the Application

```bash
# Direct
python app.py

# Windows one-click
run.bat
```

### 6. Open in Browser

Navigate to **http://localhost:5001**

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web application (SPA) |
| `POST` | `/api/chat` | Main chat with IBM Granite + RAG pipeline |
| `GET` | `/api/helplines` | 15+ verified global crisis helplines |
| `GET` | `/api/affirmation` | Random mental health affirmation |
| `GET` | `/api/topics` | Available mental health education topics |
| `GET` | `/api/topic/<id>` | Topic content + evidence-based tips |
| `GET` | `/api/breathing-exercise` | Guided breathing exercises |
| `POST` | `/api/clear-session` | Clear session history (privacy) |
| `GET` | `/api/health` | Service health check |

### Chat Request

```json
POST /api/chat
Content-Type: application/json

{
  "message": "I have been feeling really anxious and overwhelmed lately"
}
```

### Chat Response

```json
{
  "reply": "I hear you, and what you are feeling is real and valid...",
  "crisis_level": "normal",
  "emotion": "general",
  "intent": "conversation",
  "topics_found": ["Anxiety & Anxiety Disorders"],
  "status": "success"
}
```

### Crisis Response (auto-triggered, no LLM call)

```json
{
  "reply": "I hear you, and I am truly glad you reached out...",
  "crisis_level": "crisis",
  "show_helplines": true,
  "status": "success"
}
```

---

## 🛡️ AI Ethics & Safety

This application is built in strict accordance with **IBM's Ethical AI principles**:

| Principle | Implementation |
|---|---|
| ✅ **Helpful** | Evidence-based guidance from WHO, NIMH, APA, SAMHSA |
| ✅ **Accurate** | RAG-grounded responses prevent hallucinations on clinical topics |
| ✅ **Respectful (HAM)** | Trauma-informed, non-judgmental tone enforced in system prompt |
| ✅ **Safe** | 4-layer agentic safety system with immediate crisis interception |
| ✅ **Transparent** | All AI content clearly labelled; limitations stated in every session |
| ✅ **Privacy-Preserving** | Session-only storage; `POST /api/clear-session` available anytime |
| ✅ **Culturally Sensitive** | Diverse global helplines; culturally aware response generation |

### Safety Architecture

1. **Crisis Detection Agent** — Keyword gate intercepts suicidal/self-harm language, responds immediately without LLM latency
2. **Distress Elevation** — Elevated empathy mode triggered for high-distress signals
3. **Consistent Disclaimers** — Every clinical/advice response includes the AI limitation notice
4. **Input Length Limit** — Messages capped at 1,000 characters to prevent prompt injection

---

## 📚 Knowledge Base Sources

| Source | Domain |
|---|---|
| World Health Organization (WHO) | Global mental health standards |
| National Institute of Mental Health (NIMH) | Clinical research & treatment guidelines |
| American Psychological Association (APA) | Evidence-based psychological practice |
| SAMHSA | Substance use & mental health |
| Jon Kabat-Zinn MBSR Program | Mindfulness-Based Stress Reduction |
| International Association for Suicide Prevention | Crisis support |
| Cleveland Clinic / Harvard Medical School | Breathing techniques |
| National Sleep Foundation | Sleep & mental health |

---

## 🆘 Crisis Helplines

> If you or someone you know is in crisis, please use these verified helplines immediately.

| Country | Service | Contact |
|---|---|---|
| **USA** | 988 Suicide & Crisis Lifeline | Call/Text **988** |
| **USA/Global** | Crisis Text Line | Text **HOME** to **741741** |
| **UK** | Samaritans | **116 123** |
| **UK** | Mind Infoline | **0300 123 3393** |
| **India** | iCall (TISS) | **9152987821** |
| **India** | Vandrevala Foundation | **1860-2662-345** |
| **Canada** | Crisis Services Canada | **1-833-456-4566** |
| **Australia** | Lifeline | **13 11 14** |
| **Australia** | Beyond Blue | **1300 22 4636** |
| **Germany** | Telefonseelsorge | **0800 111 0 111** |
| **Singapore** | Samaritans of Singapore | **1800-221-4444** |
| **International** | IASP Directory | [iasp.info/resources/Crisis_Centres](https://www.iasp.info/resources/Crisis_Centres/) |

---

## ⚠️ Medical Disclaimer

> MindBridge AI provides **general mental health awareness information for educational purposes only**.
> It is **NOT** a licensed therapist, psychologist, psychiatrist, or medical professional.
> Information provided does not constitute medical advice, diagnosis, or treatment.
> Always consult a qualified mental health professional for personalized care.
> In a crisis, contact emergency services or a crisis helpline **immediately**.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **AI / LLM** | IBM Granite 13B Instruct v2 |
| **AI Platform** | IBM WatsonX AI (`ibm-watsonx-ai`) |
| **RAG** | Custom JSON knowledge base + semantic keyword retrieval |
| **Backend** | Python 3.x, Flask 3.x |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (SPA, 4 tabs) |
| **Typography** | Inter + Merriweather (Google Fonts) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author

**sonigutte02-gif** · [GitHub](https://github.com/sonigutte02-gif)

---

<div align="center">

*Built with compassion using IBM Granite LLM, IBM WatsonX AI & IBM Bob* 💙

*You matter. Help is always available.*

</div>
