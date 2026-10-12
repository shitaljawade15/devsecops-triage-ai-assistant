# =====================================================================
# 🖥️ MODERN ENTERPRISE FRONTEND: DEVSECOPS COPILOT
# =====================================================================

import os
import requests
import streamlit as st
import storage

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="DevSecOps Copilot | AI Release Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
storage.init_db()

# --- 2. Design System & CSS Styling ---
# --- 2. Design System & CSS Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }

    /* Top Navigation Shell */
    .top-navbar-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0f172a;
        padding: 0.85rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4);
        border: 1px solid #1e293b;
    }

    .brand-logo {
        font-size: 1.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .brand-pill {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Modern Hero Container */
    .hero-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        color: white;
        margin-bottom: 1.8rem;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.6rem;
        color: #ffffff;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 650px;
        line-height: 1.6;
        margin-bottom: 1.2rem;
    }

    /* Analytics Metric Box */
    .stat-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.3rem;
        color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    /* --- Sidebar Fix: Deep Slate Sidebar with Crisp High-Contrast Text --- */
    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Sidebar Expander & Input Contrast */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }

    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. App State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["current_thread_id"] = None
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Home"


# =====================================================================
# 🧭 TOP NAVIGATION BAR
# =====================================================================
nav_user_badge = f"👤 @{st.session_state['username']}" if st.session_state["logged_in"] else "🔒 Guest Mode"

st.markdown(f"""
<div class="top-navbar-wrapper">
    <div class="brand-logo">
        <span>🛡️ DevSecOps Copilot</span>
        <span class="brand-pill">Enterprise</span>
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600;">
        {nav_user_badge}
    </div>
</div>
""", unsafe_allow_html=True)

# Sticky Tab Controls
nav_cols = st.columns([1.5, 1.6, 1.4, 1.4, 1.6])

with nav_cols[0]:
    if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state["active_nav"] == "Home" else "secondary"):
        st.session_state["active_nav"] = "Home"
        st.rerun()

with nav_cols[1]:
    if st.button("💬 New Chat", use_container_width=True, type="primary" if st.session_state["active_nav"] == "Chat" else "secondary"):
        st.session_state["active_nav"] = "Chat"
        st.rerun()

with nav_cols[2]:
    if st.button("📖 About", use_container_width=True, type="primary" if st.session_state["active_nav"] == "About" else "secondary"):
        st.session_state["active_nav"] = "About"
        st.rerun()

with nav_cols[3]:
    if st.button("📬 Contact", use_container_width=True, type="primary" if st.session_state["active_nav"] == "Contact" else "secondary"):
        st.session_state["active_nav"] = "Contact"
        st.rerun()

with nav_cols[4]:
    if st.session_state["logged_in"]:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["current_thread_id"] = None
            st.session_state["active_nav"] = "Home"
            st.rerun()
    else:
        if st.button("🔑 Login / Sign Up", use_container_width=True, type="primary" if st.session_state["active_nav"] == "Auth" else "secondary"):
            st.session_state["active_nav"] = "Auth"
            st.rerun()

st.markdown("<hr style='margin: 0.4rem 0 1.5rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


# =====================================================================
# 🏠 TAB 1: HOME PAGE
# =====================================================================
if st.session_state["active_nav"] == "Home":
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">Automate Security Triage & Release Gating</div>
        <div class="hero-subtitle">
            An intelligent DevSecOps Copilot engineered to ingest SAST, SCA, and secret detection reports,
            evaluate production reachability, cross-check waivers, and deliver concrete remediation commands.
        </div>
    </div>
    """, unsafe_allow_html=True)

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">768-D</div>
            <div class="stat-label">Vector Semantic Search</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">100%</div>
            <div class="stat-label">Thread & Tenant Isolation</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">Multi-Format</div>
            <div class="stat-label">JSON, SARIF, PDF, CSV, TXT</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">Instant</div>
            <div class="stat-label">Automated Remediation Fixes</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    st.subheader("⚡ Quick Start Actions")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        st.markdown("#### 🎯 Launch Workspace")
        st.write("Jump straight into an isolated project workspace to upload vulnerability scans and triage critical findings.")
        if st.button("Open Active Chat Workspace →", use_container_width=True, type="primary"):
            st.session_state["active_nav"] = "Chat"
            st.rerun()

    with action_col2:
        st.markdown("#### 📑 Explore Capabilities")
        st.write("Review the underlying RAG architecture, vector embeddings pipeline, and Nugen fine-tuned model specifications.")
        if st.button("View System Architecture →", use_container_width=True):
            st.session_state["active_nav"] = "About"
            st.rerun()


# =====================================================================
# 💬 TAB 2: CHAT & PROJECT THREAD WORKSPACE
# =====================================================================
elif st.session_state["active_nav"] == "Chat":
    if not st.session_state["logged_in"]:
        st.info("🔒 **Authentication Required:** Please sign in or register to access isolated project threads and vectorize documents.")
        if st.button("Proceed to Login / Sign Up →", type="primary"):
            st.session_state["active_nav"] = "Auth"
            st.rerun()
    else:
        username = st.session_state["username"]
        threads = storage.get_user_threads(username)
        if not threads:
            default_id = storage.create_thread(username, "General Release Triage")
            st.session_state["current_thread_id"] = default_id
            threads = storage.get_user_threads(username)

        thread_dict = {t["thread_id"]: t for t in threads}
        if st.session_state.get("current_thread_id") not in thread_dict:
            st.session_state["current_thread_id"] = threads[0]["thread_id"]

        active_id = st.session_state["current_thread_id"]
        active_thread = thread_dict[active_id]
        active_title = active_thread.get("title", "General Triage")

        # Sidebar: Thread Management & File Ingestion
        with st.sidebar:
            st.subheader("📁 Project Threads")
            st.caption("Each thread maintains an isolated vector space.")

            thread_options = list(thread_dict.keys())
            selected_tid = st.selectbox(
                "Active Thread:",
                options=thread_options,
                format_func=lambda tid: f"{'📌 ' if thread_dict[tid].get('is_pinned', False) else '💬 '}{thread_dict[tid].get('title', 'Thread')}",
                index=thread_options.index(active_id)
            )

            if selected_tid != active_id:
                st.session_state["current_thread_id"] = selected_tid
                st.rerun()

            # Thread Actions
            with st.expander("⚙️ Thread Settings"):
                is_pinned = active_thread.get("is_pinned", False)
                pin_label = "📍 Unpin Thread" if is_pinned else "📌 Pin Thread"
                if st.button(pin_label, use_container_width=True):
                    storage.toggle_pin_thread(active_id)
                    st.rerun()

                new_title_val = st.text_input("Rename Thread", value=active_title).strip()
                if st.button("💾 Save Name", use_container_width=True):
                    if new_title_val and new_title_val != active_title:
                        storage.rename_thread(active_id, new_title_val)
                        st.success("Renamed!")
                        st.rerun()

                st.markdown("---")
                if st.button("🗑️ Delete Thread", type="secondary", use_container_width=True):
                    if len(threads) <= 1:
                        st.error("Cannot delete the only remaining thread.")
                    else:
                        storage.delete_thread(active_id)
                        remaining = storage.get_user_threads(username)
                        st.session_state["current_thread_id"] = remaining[0]["thread_id"]
                        st.rerun()

            # Create Thread
            with st.expander("➕ Create New Thread"):
                new_project_name = st.text_input("New Thread Name", placeholder="e.g. Auth Service SCA").strip()
                if st.button("Create Thread", use_container_width=True):
                    if new_project_name:
                        created_id = storage.create_thread(username, new_project_name)
                        st.session_state["current_thread_id"] = created_id
                        st.success("Thread initialized!")
                        st.rerun()

            st.markdown("---")
            st.subheader("📥 Ingest Scan Artifact")
            st.caption("Scoped strictly to the current thread.")
            uploaded_file = st.file_uploader(
                "Upload Audit Document",
                type=["pdf", "json", "csv", "txt", "log", "yaml", "yml", "sarif"]
            )

            if st.button("⚡ Vectorize & Ingest", use_container_width=True, type="primary"):
                if uploaded_file is not None:
                    with st.spinner("Chunking & embedding..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                            form_data = {"username": username, "thread_id": active_id}
                            res = requests.post(f"{BASE_API_URL}/upload-file", files=files, data=form_data, timeout=120)
                            if res.ok:
                                data = res.json()
                                st.success(f"✅ Indexed {data['chunks_indexed']} chunks from `{data['filename']}`!")
                            else:
                                st.error(f"Upload failed: {res.text}")
                        except Exception as e:
                            st.error(f"Backend offline: {str(e)}")
                else:
                    st.warning("Select a file first.")

        # Main Chat View
        pin_prefix = "📌 " if active_thread.get("is_pinned", False) else ""
        st.markdown(f"### 🛡️ {pin_prefix}**{active_title}**")
        st.caption(f"Thread ID: `{active_id}` | Grounded only on scans uploaded to this project.")

        thread_messages = storage.get_thread_messages(active_id)
        if not thread_messages:
            st.info("💡 **Ready to triage:** Upload a report in the sidebar or ask general DevSecOps release policy questions below.")

        for msg in thread_messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        user_query = st.chat_input(f"Ask Copilot about {active_title}...")

        if user_query:
            storage.add_message(active_id, "user", user_query)
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_query)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Evaluating release gating & context..."):
                    try:
                        res = requests.post(
                            f"{BASE_API_URL}/chat",
                            json={
                                "username": username,
                                "thread_id": active_id,
                                "question": user_query,
                                "top_k": 3
                            },
                            timeout=60
                        )
                        if res.ok:
                            data = res.json()
                            answer = data.get("answer", "")
                            sources = data.get("sources_used", [])

                            st.markdown(answer)
                            if sources and sources[0] != "No uploaded documents found for this specific thread.":
                                with st.expander("🔍 View Retrieved Context Evidence"):
                                    for idx, src in enumerate(sources, 1):
                                        st.markdown(f"**Evidence Chunk {idx}:**\n```\n{src}\n```")

                            storage.add_message(active_id, "assistant", answer)
                        else:
                            st.error(f"Triage error: {res.text}")
                    except Exception as e:
                        st.error(f"Backend offline: {str(e)}")


# =====================================================================
# 📖 TAB 3: ABOUT TAB
# =====================================================================
elif st.session_state["active_nav"] == "About":
    st.markdown("### 📖 About DevSecOps Copilot")
    st.markdown("""
    **DevSecOps Copilot** is a production-aligned security assistant built to bridge static code analysis,
    container vulnerability scanning, and real-time release gating decisions.
    """)

    st.markdown("#### 🏗️ Technical Stack")
    stack_col1, stack_col2 = st.columns(2)
    with stack_col1:
        st.markdown("""
        - **Backend:** FastAPI (Python 3.11+)
        - **Frontend:** Streamlit with modern custom CSS styling
        - **Vector Store:** Qdrant In-Memory (`:memory:`)
        - **Vector Space:** 768 Dimensions with Cosine Similarity
        """)
    with stack_col2:
        st.markdown("""
        - **Inference Engine:** Nugen Cloud (`model_01m370f1zcf3wswn`)
        - **Query Optimization:** Custom DevSecOps semantic enhancer
        - **Database:** SQLite for multi-tenant threads & chat persistence
        - **Supported Scanners:** Trivy, Semgrep, Gitleaks, Checkov, CISA KEV
        """)

    st.markdown("---")
    st.markdown("#### 🔄 Pipeline Topology")
    st.code("""
[ Scan Report / Policy ] ──> [ Universal Extractor ] ──> [ Nugen Embeddings (768-d) ]
                                                                   │
                                                                   ▼
[ Developer Query ] ──> [ Query Enhancer ] ──> [ Qdrant Vector DB (Thread Scoped) ]
                                                       │
                                                       ▼
                               [ Fine-Tuned LLM (Nugen Cloud) ]
                                                       │
                                                       ▼
                                [ Grounded Triage & Fix Commands ]
    """, language="text")


# =====================================================================
# 📬 TAB 4: CONTACT TAB
# =====================================================================
elif st.session_state["active_nav"] == "Contact":
    st.markdown("### 📬 Contact & Support")
    st.markdown("Have questions, feedback, or need enterprise pipeline integrations? Reach out below.")

    c_col1, c_col2 = st.columns([1.5, 1])
    with c_col1:
        with st.form("contact_form"):
            name = st.text_input("Full Name", placeholder="Alex Mercer")
            email = st.text_input("Work Email", placeholder="alex@company.com")
            subject = st.selectbox("Topic", ["Pipeline Integration", "Custom Model Fine-Tuning", "Report an Issue", "General Feedback"])
            message = st.text_area("Message", placeholder="Describe your question or requirements...", height=130)
            submitted = st.form_submit_button("Send Inquiry →", use_container_width=True, type="primary")

            if submitted:
                if name and email and message:
                    st.success("✅ Thank you! Your message has been logged. We will get back to you shortly.")
                else:
                    st.warning("Please fill out all required fields.")

    with c_col2:
        st.markdown("""
        <div class="stat-card" style="margin-top: 1.8rem;">
            <h4 style="margin-bottom: 0.5rem;">DevSecOps Engineering</h4>
            <p style="color: #64748b; font-size: 0.9rem;">
                This solution is built for engineering teams seeking faster security reviews without bottlenecking CI/CD pipelines.
            </p>
            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 0.8rem 0;">
            <div style="font-size: 0.85rem; color: #475569;">
                <b>Documentation:</b> Check project <code>README.md</code><br>
                <b>Status:</b> All Core Services Operational 🟢<br>
                <b>Release:</b> v1.2.0 Enterprise
            </div>
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# 🔐 TAB 5: LOGIN / SIGN UP VIEW
# =====================================================================
elif st.session_state["active_nav"] == "Auth":
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.8rem; margin-bottom: 0.2rem;">🔐 Workspace Access</h2>
            <p style="color: #64748b; font-size: 0.95rem;">Sign in or create an account to access project threads</p>
        </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "🚀 Register Account"])

        with auth_tab1:
            with st.form("signin_form"):
                l_user = st.text_input("Username").strip()
                l_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submit_login:
                    if l_user and l_pass:
                        if storage.verify_user(l_user, l_pass):
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = l_user
                            st.session_state["active_nav"] = "Chat"
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                    else:
                        st.warning("Enter both username and password.")

        with auth_tab2:
            with st.form("signup_form"):
                s_user = st.text_input("Choose Username").strip()
                s_pass = st.text_input("Choose Password", type="password")
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)

                if submit_signup:
                    if s_user and s_pass:
                        if len(s_pass) < 4:
                            st.error("Password must be at least 4 characters.")
                        elif storage.register_user(s_user, s_pass):
                            st.success("Account created successfully! Please sign in.")
                        else:
                            st.error("Username already taken.")
                    else:
                        st.warning("All fields are required.")