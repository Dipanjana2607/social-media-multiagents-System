# Social Media MultiAgent System — Agentic AI for Creators

Turning social content planning into product-grade automation. Social Media Agent is an agentic AI platform that coordinates Planner, Executor, and Verifier agents to research, draft, and validate social posts across platforms (Instagram, Twitter/X, LinkedIn).

---

## Why it matters

- **Problem:** Content teams waste time iterating, fact-checking, and producing platform-tailored posts.
- **Solution:** An agentic system that plans strategy, executes drafts using LLMs, and verifies quality & safety automatically — saving time and improving consistency.

---

## Product Snapshot

- **Who:** Small content teams, startups, marketing freelancers.
- **What:** Research-driven, multi-platform content drafts with built-in verification and edit suggestions.
- **How:** Three specialized agents collaborate: Planner → Executor → Verifier.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Google Gemini 2.5 Flash | Powers all three agents (Planner, Executor, Verifier) |
| **LLM Framework** | LangChain (`langchain`, `langchain-google-genai`) | Wraps Gemini with `ChatGoogleGenerativeAI`, manages `SystemMessage` / `HumanMessage` formatting |
| **Backend** | FastAPI | REST API server — exposes `/api/v1/content/generate` and `/api/v1/content/platforms` |
| **ASGI Server** | Uvicorn | Runs the FastAPI app with hot-reload in development |
| **Data Validation** | Pydantic + pydantic-settings | Validates request/response DTOs and reads `.env` config |
| **Frontend** | Streamlit | Browser UI — platform selector, topic input, live agent pipeline trace |
| **HTTP Client** | Requests | Streamlit calls the FastAPI backend over HTTP |
| **Environment Config** | python-dotenv | Loads `GOOGLE_API_KEY` from `.env` securely |
| **Runtime** | Python 3.10+ | All backend and frontend code |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                       │
│  User selects platform, enters topic, clicks Generate    │
└─────────────────────┬────────────────────────────────────┘
                      │  HTTP POST /api/v1/content/generate
                      ▼
┌──────────────────────────────────────────────────────────┐
│              FastAPI  (content_controller.py)             │
│  Validates request with Pydantic DTOs                    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│              ContentService  (content_service.py)         │
│                                                          │
│  1. Calls prompt_registry → loads platform prompts       │
│  2. Runs Planner Agent   → produces content plan         │
│  3. Runs Executor Agent  → writes the full post          │
│  4. Runs Verifier Agent  → checks quality & safety       │
│  5. If FAIL → retries Executor (or full restart)         │
│  6. Returns final content + full agent trace             │
└──────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐
  │  Planner   │  │   Executor   │  │    Verifier     │
  │  Agent     │  │   Agent      │  │    Agent        │
  │            │  │              │  │                 │
  │ Builds     │  │ Writes full  │  │ Checks quality  │
  │ content    │→ │ post from    │→ │ PASS → return   │
  │ plan       │  │ plan         │  │ FAIL → retry    │
  └────────────┘  └──────────────┘  └─────────────────┘
         │                │                │
         └────────────────┴────────────────┘
                          │  All agents receive prompts from:
                          ▼
┌──────────────────────────────────────────────────────────┐
│                 Prompt Registry                           │
│                                                          │
│  "linkedin"  → linkedin_prompts.py  (planner/exec/verif) │
│  "twitter"   → twitter_prompts.py   (planner/exec/verif) │
│  "instagram" → instagram_prompts.py (planner/exec/verif) │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              LLM Factory  (llm_factory.py)                │
│  ChatGoogleGenerativeAI (Gemini 1.5 Flash)               │
│  Google API Key loaded from .env                         │
└──────────────────────────────────────────────────────────┘
```

### Folder Structure

```
social_media_agents/
├── backend/
│   ├── .env                          ← API keys (never commit this)
│   ├── run.py                        ← starts Uvicorn server
│   └── app/
│       ├── config.py                 ← reads .env via pydantic-settings
│       ├── main.py                   ← FastAPI app + router registration
│       ├── agents/
│       │   ├── base_agent.py         ← abstract base (shared _call_llm logic)
│       │   ├── planner_agent.py      ← generic planner (platform-agnostic)
│       │   ├── executor_agent.py     ← generic executor (platform-agnostic)
│       │   └── verifier_agent.py     ← generic verifier + PASS/FAIL parser
│       ├── prompts/
│       │   ├── linkedin_prompts.py   ← planner/executor/verifier prompts for LinkedIn
│       │   ├── twitter_prompts.py    ← planner/executor/verifier prompts for Twitter
│       │   ├── instagram_prompts.py  ← planner/executor/verifier prompts for Instagram
│       │   └── prompt_registry.py    ← maps platform name → correct prompts dict
│       ├── services/
│       │   └── content_service.py    ← orchestrates agents + retry logic
│       ├── controllers/
│       │   └── content_controller.py ← HTTP endpoints (/generate, /platforms)
│       ├── dtos/
│       │   ├── request_dtos.py       ← GenerateContentRequest (Pydantic)
│       │   └── response_dtos.py      ← GenerateContentResponse, AgentStepResult
│       └── utils/
│           └── llm_factory.py        ← builds ChatGoogleGenerativeAI instance
└── frontend/
    └── app.py                        ← Streamlit UI
```

### Key Design Decisions

**3 generic agents + N prompt files** — Agents (`PlannerAgent`, `ExecutorAgent`, `VerifierAgent`) contain zero platform-specific knowledge. All platform rules live in the prompts files. Adding a new platform (e.g. TikTok) requires only creating `tiktok_prompts.py` and adding one line to the registry — no agent code changes.

**Prompt Registry as dynamic router** — `prompt_registry.py` maps the platform string from the request body (`"linkedin"`, `"twitter"`, `"instagram"`) to the correct prompt dictionary at runtime. This is how platform selection works dynamically.

**Verifier-driven retry loop** — the `ContentService` runs a `while` loop up to `max_retries` times. On FAIL, the verifier signals either `RESTART_STAGE: PLANNER` (full restart) or `RESTART_STAGE: EXECUTOR` (cheaper retry — reuse the plan, just rewrite the post with feedback injected).

---

## Agent Responsibilities

### 1. Planner Agent (`planner_agent.py`)
- Receives: user brief (topic, tone, platform, extra instructions)
- Produces: structured content plan — hook, key points, CTA, hashtag strategy
- Temperature: `0.6` (structured, moderate creativity)

### 2. Executor Agent (`executor_agent.py`)
- Receives: the Planner's content plan
- Produces: complete platform-specific post (full text, hashtags, emojis where appropriate)
- Temperature: `0.8` (more creative — writing the actual content)

### 3. Verifier Agent (`verifier_agent.py`) — the quality gate
- Receives: the Executor's draft + original plan + topic
- Checks: word count, platform constraints, tone match, hashtag count, CTA presence
- Produces: `VERDICT: PASS` or `VERDICT: FAIL` with `RESTART_STAGE` and `FEEDBACK`
- Temperature: `0.2` (very low — consistent, strict judgements)

---

## Getting Started

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd social_media_agents

python -m venv venv
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install fastapi "uvicorn[standard]" langchain langchain-google-genai \
            google-generativeai python-dotenv pydantic pydantic-settings \
            streamlit requests
```

### 2. Create your `.env` file

```bash
# inside backend/.env
google_api_key=your_google_api_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com) → Get API Key.

### 3. Run the backend

```bash
cd backend
python run.py
# Server starts at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### 4. Run the frontend

```bash
# In a second terminal (same venv activated)
cd frontend
streamlit run app.py
# Opens automatically at http://localhost:8501
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/content/generate` | Run the full agent pipeline for a platform |
| `GET` | `/api/v1/content/platforms` | List all supported platforms |
| `GET` | `/health` | Server health check |

**Request body for `/generate`:**
```json
{
  "platform": "linkedin",
  "topic": "Why developers should learn system design",
  "tone": "professional",
  "extra_instructions": "Keep it under 250 words",
  "max_retries": 2
}
```

---

## Customizing the LLM Provider

The LLM connection lives entirely in `backend/app/utils/llm_factory.py`. To swap to OpenAI or Anthropic:

1. Update `llm_factory.py` with the new provider's LangChain class
2. Add the new API key to `.env`
3. No other files need to change

---

## Extensibility

- **Add a new platform:** Create `backend/app/prompts/tiktok_prompts.py` and add one line to `prompt_registry.py`
- **Add new verifier checks:** Extend the verifier prompt in the platform's prompts file
- **Add analytics:** Post-process the `GenerateContentResponse` after the verifier step in `content_service.py`

> Built with ❤️ by Dipanjana Das
