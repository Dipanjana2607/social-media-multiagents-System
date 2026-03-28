import streamlit as st
import requests
import threading
import time
import queue

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Social Agent Studio", page_icon="🤖", layout="wide")
st.title("🤖 Social Media Multi-Agent Studio")
st.caption("Agentic AI System · Planner → Executor → Verifier · Powered by Gemini · Dynamic platform selection")

# ── Fetch available platforms dynamically from the backend ──────────────────
# This means: if you add a new platform to the registry, the frontend updates automatically
# @st.cache_data tells Streamlit: "only call this function once, then cache the result"
# ttl=3600 means "refresh the cache every 3600 seconds (1 hour)"
@st.cache_data(ttl=3600)
def fetch_platforms() -> list[str]:
    """Call the backend's /platforms endpoint and return the list."""
    try:
        resp = requests.get(f"{API_BASE}/content/platforms", timeout=5)
        # resp.json() parses the JSON: {"platforms": ["linkedin", "twitter", "instagram"]}
        # ["platforms"] gets the list value
        return resp.json()["platforms"]
    except Exception:
        # If backend is unreachable, fall back to hardcoded list so UI still works
        return ["linkedin", "twitter", "instagram"]

# ── Icons map — display name → icon ─────────────────────────────────────────
PLATFORM_ICONS = {
    "linkedin":  "💼",
    "twitter":   "🐦",
    "instagram": "📸",
}

platforms = fetch_platforms()   # ["linkedin", "twitter", "instagram"]

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Build display labels with icons: "💼 linkedin", "🐦 twitter", etc.
    # This is a list comprehension — a compact way to build a list with a loop
    # For each p in platforms: create the string f"{icon} {p.title()}"
    platform_labels = [
        f"{PLATFORM_ICONS.get(p, '🌐')} {p.title()}" for p in platforms
    ]
    # .get(p, '🌐') — if no icon found for platform p, use a globe emoji as default
    # .title() — "linkedin" → "LinkedIn"
    
    selected_label = st.selectbox("Platform", platform_labels)
    
    # Reverse-map the label back to the raw platform string
    # "💼 LinkedIn" → index 0 → platforms[0] = "linkedin"
    selected_index = platform_labels.index(selected_label)
    platform = platforms[selected_index]

    tone = st.selectbox(
        "Tone",
        ["professional", "casual", "inspirational", "humorous", "educational"]
    )
    max_retries = st.slider("Max verifier retries", 1, 5, 2)
    st.divider()
    st.info("Not a typical API call — multiple collaborating agents (Planner → Executor → Verifier) work together as an Agentic AI system to generate content for you.")

# Ensure session state keys exist
if "in_progress" not in st.session_state:
    st.session_state["in_progress"] = False
if "response_data" not in st.session_state:
    st.session_state["response_data"] = None
if "result_queue" not in st.session_state:
    st.session_state["result_queue"] = None

# ── Main content area ────────────────────────────────────────────────────────
icon = PLATFORM_ICONS.get(platform, "🌐")
st.subheader(f"{icon} Generate {platform.title()} Content")

topic = st.text_area(
    "What's your topic or idea?",
    placeholder="e.g. Why every developer should learn system design"
)
extra = st.text_input(
    "Extra instructions (optional)",
    placeholder="e.g. Keep it concise, mention real-world examples"
)

button_label = "🚀 Generating..." if st.session_state["in_progress"] else "🚀 Generate Content"
generate_clicked = st.button(button_label, use_container_width=True, type="primary", disabled=st.session_state["in_progress"])

if generate_clicked:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        if st.session_state["in_progress"]:
            st.info("Request already in progress — please wait.")
        else:
            # Build the request payload
            payload = {
                "platform": platform,
                "topic": topic,
                "tone": tone,
                "extra_instructions": extra,
                "max_retries": max_retries,
            }

            # Worker: call backend and put result into a queue
            def call_backend(payld, q):
                try:
                    resp = requests.post(f"{API_BASE}/content/generate", json=payld, timeout=120)
                    try:
                        body = resp.json()
                    except Exception:
                        body = {"detail": "Invalid JSON from server"}
                    q.put({"ok": True, "status_code": resp.status_code, "body": body})
                except Exception as e:
                    q.put({"ok": False, "error": str(e)})

            # Prepare state and start background thread
            st.session_state["in_progress"] = True
            result_q = queue.Queue()
            st.session_state["result_queue"] = result_q
            worker = threading.Thread(target=call_backend, args=(payload, result_q), daemon=True)
            worker.start()

            # Show looping loading stages until the worker finishes
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            statuses = ["Planning", "Executing", "Verifying"]

            while worker.is_alive():
                for status in statuses:
                    if not worker.is_alive():
                        break
                    with status_placeholder.container():
                        st.info(f"{status}...")
                    prog = progress_placeholder.progress(0)
                    # each status lasts ~3 seconds split into 30 steps
                    for i in range(30):
                        if not worker.is_alive():
                            break
                        prog.progress((i + 1) / 30)
                        time.sleep(0.1)

            # Worker finished — retrieve result
            try:
                result = result_q.get_nowait()
            except Exception:
                result = {"ok": False, "error": "No response from worker"}

            st.session_state["in_progress"] = False

            # Clear placeholders
            status_placeholder.empty()
            progress_placeholder.empty()

            # Handle result
            if not result.get("ok"):
                err = result.get("error", "Unknown error")
                if "Timeout" in err:
                    st.error("Request timed out — agents are taking too long. Try again.")
                elif "Connection" in err or "ConnectionError" in err:
                    st.error("Cannot connect to backend. Is FastAPI running on port 8000?")
                else:
                    st.error(f"Unexpected error: {err}")
            else:
                resp_status = result.get("status_code", 0)
                data = result.get("body", {})

                if resp_status == 400:
                    st.error(f"Bad request: {data.get('detail', 'Unknown error')}")
                    st.stop()
                elif resp_status != 200:
                    st.error(f"Server error ({resp_status}). Try again.")
                    st.stop()

                # Show result
                if data.get("success"):
                    st.success(f"✅ Approved after {data['total_attempts']} attempt(s)")
                else:
                    st.warning("⚠️ Max retries reached — showing best attempt.")

                st.subheader("📄 Final Content")
                st.text_area("Copy this content", value=data.get("final_content", ""), height=300)

                st.subheader("🔍 Agent Pipeline Trace")
                for step in data.get("steps", []):
                    label = f"[Attempt {step.get('attempt')}] {step.get('agent')}"
                    with st.expander(label):
                        st.text(step.get("output", ""))