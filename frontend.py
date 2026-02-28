"""
╔══════════════════════════════════════════════════════════════╗
║         MindCare Assistant — FRONTEND (Streamlit)           ║
║         Domain: Mental Health & Emotional Wellness          ║
║         Run: streamlit run frontend.py                      ║
║         Requires backend.py running on port 8000            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests

# ─── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MindCare Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

/* GLOBAL TEXT COLOR FIX */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #111111 !important;
}

.stApp {
    background: #f8f5ef;
    color: #111111 !important;
}

/* SIDEBAR TEXT FIX */
[data-testid="stSidebar"] {
    background: #fdfbf7 !important;
    border-right: 1px solid #e8e2d8;
    color: #111111 !important;
}

/* Force sidebar text dark */
[data-testid="stSidebar"] * {
    color: #111111 !important;
}

/* HEADER */
.main-header {
    background: linear-gradient(135deg, #4a7459 0%, #7a9e87 100%);
    color: white !important;
    padding: 22px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
}
.main-header h1 {
    font-family: 'Lora', serif;
    font-size: 26px;
    font-weight: 600;
    margin: 0;
    color: white !important;
}
.main-header p {
    margin: 4px 0 0;
    font-size: 13px;
    opacity: 0.9;
    color: white !important;
}

/* CHAT BUBBLES */
.user-bubble {
    background: #4a7459;
    color: white !important;
    padding: 13px 17px;
    border-radius: 16px 16px 4px 16px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.65;
}

.ai-bubble {
    background: #ffffff;
    border: 1px solid #e8e2d8;
    padding: 16px 20px;
    border-radius: 16px 16px 16px 4px;
    max-width: 84%;
    font-size: 14px;
    line-height: 1.75;
    color: #111111 !important;
}

/* EMPTY STATE */
.empty-state {
    text-align: center;
    padding: 64px 20px;
    color: #111111 !important;
}
.empty-state h3 {
    font-family: 'Lora', serif;
    color: #111111 !important;
    font-size: 22px;
    margin: 12px 0 8px;
}

/* BUTTON TEXT */
.stButton > button {
    width: 100%;
    text-align: left;
    background: #ffffff;
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: #111111 !important;
}

/* TEXT AREA FIX */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e8e2d8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    background: #ffffff !important;
    color: #111111 !important;
}

/* FOOTER FIX */
div[style*="text-align:center"] {
    color: #111111 !important;
}
</style>
""", unsafe_allow_html=True)
# ─── Sample Queries ────────────────────────────────────────────────────────────
IN_DOMAIN = [
    "I've been feeling very anxious lately and can't calm down.",
    "What are beginner mindfulness techniques I can try today?",
    "I can't sleep due to racing thoughts. Any tips?",
    "Can you teach me a breathing exercise for work stress?",
    "What's the difference between stress and anxiety?",
    "I've felt sad and unmotivated for weeks. Is this depression?",
    "When should I consider seeing a therapist?",
    "How can journaling help with emotional regulation?",
]

OUT_OF_DOMAIN = [
    "What medication should I take for a headache?",
    "Write me a Python script to sort a list.",
    "What's the best diet for weight loss?",
]

# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = ""


# ─── Backend Health Check ──────────────────────────────────────────────────────
def check_backend():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def send_to_backend(query: str, model: str, temperature: float):
    r = requests.post(
        f"{BACKEND_URL}/chat",
        json={"query": query, "model": model, "temperature": temperature},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["response"]


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 MindCare")
    st.markdown("**Mental Health & Wellness AI**")

    # Backend status
    backend_alive = check_backend()
    if backend_alive:
        st.markdown('<div class="status-ok">🟢 Backend Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">🔴 Backend Offline</div>', unsafe_allow_html=True)
        st.caption("Start backend: `uvicorn backend:app --reload`")

    st.markdown("---")

    # Model
    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    model = st.selectbox("", [
        "openai/gpt-3.5-turbo",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku",
        "mistralai/mistral-7b-instruct",
        "meta-llama/llama-3-8b-instruct",
    ], label_visibility="collapsed")

    # Temperature
    st.markdown('<div class="sidebar-label">Temperature</div>', unsafe_allow_html=True)
    temperature = st.slider("", 0.0, 1.0, 0.3, 0.1, label_visibility="collapsed")
    label = "🎯 Precise & Structured" if temperature <= 0.3 else ("⚖️ Balanced" if temperature <= 0.6 else "💬 Creative & Conversational")
    st.caption(f"{label}  ({temperature})")

    st.markdown("---")

    # In-domain samples
    st.markdown('<div class="sidebar-label">✅ In-Domain Queries</div>', unsafe_allow_html=True)
    for q in IN_DOMAIN:
        if st.button(q, key=f"in_{q[:25]}"):
            st.session_state.pending = q

    # Out-of-domain samples
    st.markdown('<div class="sidebar-label">⚠️ Out-of-Domain Tests</div>', unsafe_allow_html=True)
    for q in OUT_OF_DOMAIN:
        if st.button(f"⚠️ {q}", key=f"out_{q[:25]}"):
            st.session_state.pending = q

    st.markdown("---")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# ─── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div style="display:flex;align-items:center;gap:16px">
        <div style="font-size:42px">🧠</div>
        <div>
            <h1>MindCare Assistant</h1>
            <p>Compassionate AI for mental health & emotional wellness · Powered by OpenRouter + LangChain</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Chat History ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:52px">🌿</div>
        <h3>How can I support you today?</h3>
        <p>Ask about anxiety, mindfulness, sleep, emotional wellness, and more.
        Use the sidebar to pick a sample query or type your own below.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-row">
                <div class="user-bubble">{msg["content"]}</div>
                <div class="avatar avatar-user">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-row">
                <div class="avatar avatar-ai">🧠</div>
                <div class="ai-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── Input ─────────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_area(
        "",
        value=st.session_state.pending,
        placeholder="Ask about anxiety, mindfulness, sleep, emotional wellness...",
        height=80,
        label_visibility="collapsed",
        key="chat_input"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send = st.button("Send ➤", use_container_width=True, key="send_btn")

# ─── Send Logic ────────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.pending = ""

    if not backend_alive:
        st.error("❌ Backend is not running. Start it with: `uvicorn backend:app --reload`")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        with st.spinner("MindCare is thinking..."):
            try:
                reply = send_to_backend(user_input.strip(), model, temperature)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**⚠️ Error:** {str(e)}"
                })
        st.rerun()

elif st.session_state.pending:
    st.session_state.pending = ""
    st.rerun()

st.markdown("""
<div style="text-align:center;padding:16px 0 4px;font-size:12px;color:#7a7a80;">
    🌿 MindCare · Mental Health & Wellness Domain · Frontend → Backend Architecture
</div>
""", unsafe_allow_html=True)
