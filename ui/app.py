"""
Project TITAN — Dashboard
A polished, product-site-style front end for building software from a prompt.
"""

import time
import json
import sys
import os
import threading
from pathlib import Path

import streamlit as st
import requests

# ── Page Config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project TITAN",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --bg: #0B0D12;
        --surface: #12151C;
        --surface-2: #171B24;
        --border: #232838;
        --border-strong: #2E3548;
        --text: #E5E7EB;
        --text-muted: #8A93A6;
        --text-faint: #5B6478;
        --accent: #5B6EF5;
        --accent-soft: rgba(91,110,245,0.10);
        --accent-strong: #7C8CF8;
        --success: #34D399;
        --error: #F87171;
        --warning: #FBBF24;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: var(--bg); color: var(--text); }

    #MainMenu, footer, header { visibility: hidden; }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 3.5rem 1rem 3rem;
        max-width: 760px;
        margin: 0 auto;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 100px;
        border: 1px solid var(--border-strong);
        background: var(--surface);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--accent-strong);
        margin-bottom: 1.4rem;
    }

    .hero-badge .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--success);
    }

    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: var(--text);
        margin: 0 0 1.1rem 0;
    }

    .hero p {
        font-size: 1.1rem;
        color: var(--text-muted);
        line-height: 1.6;
        max-width: 560px;
        margin: 0 auto;
    }

    /* ── Section label ── */
    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-faint);
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* ── Cards ── */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.6rem 1.5rem;
        height: 100%;
        transition: border-color 0.15s ease;
    }

    .metric-card:hover { border-color: var(--border-strong); }

    .metric-card .step-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: var(--accent-strong);
        letter-spacing: 0.08em;
        margin-bottom: 0.7rem;
    }

    .metric-card h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        margin: 0 0 0.5rem 0;
    }

    .metric-card p {
        color: var(--text-muted);
        font-size: 0.87rem;
        line-height: 1.5;
        margin: 0;
    }

    /* ── Build panel ── */
    .build-panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        max-width: 760px;
        margin: 0 auto;
    }

    /* ── Agent badges ── */
    .agent-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 5px;
        font-size: 0.7rem;
        font-weight: 500;
        font-family: 'IBM Plex Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        background: var(--surface-2);
        color: var(--text-muted);
        border: 1px solid var(--border);
    }

    .agent-badge .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }

    .dot-planner { background: #7C8CF8; }
    .dot-code { background: #34D399; }
    .dot-testing { background: #FBBF24; }
    .dot-docs { background: #C084FC; }
    .dot-github { background: #F472B6; }
    .dot-filesystem { background: #38BDF8; }
    .dot-terminal { background: #FB923C; }
    .dot-titan { background: #8A93A6; }
    .dot-vscode { background: #60A5FA; }

    /* ── Build log ── */
    .event-log {
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.5rem 0.9rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        max-height: 340px;
        overflow-y: auto;
    }

    .event-line {
        padding: 7px 0;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .event-line:last-child { border-bottom: none; }

    /* ── Input ── */
    .stTextArea textarea {
        background: var(--bg) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }

    .stTextInput input {
        background: var(--bg) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: 1px solid var(--accent) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1.5rem !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background: var(--accent-strong) !important;
        border-color: var(--accent-strong) !important;
    }

    .stButton > button:disabled {
        background: var(--surface-2) !important;
        border-color: var(--border) !important;
        color: var(--text-faint) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0A0C11 !important;
        border-right: 1px solid var(--border) !important;
    }

    .brand {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.01em;
        padding: 0.4rem 0 1rem 0;
    }

    .nav-item {
        color: var(--text-muted);
        font-size: 0.88rem;
        padding: 0.5rem 0;
    }

    .project-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
        font-size: 0.85rem;
    }

    .project-row:last-child { border-bottom: none; }

    /* ── Progress ── */
    .stProgress > div > div { background: var(--accent) !important; border-radius: 100px !important; }

    /* ── Result banner ── */
    .success-banner {
        background: var(--surface);
        border: 1px solid var(--success);
        border-left: 3px solid var(--success);
        border-radius: 12px;
        padding: 1.6rem 1.8rem;
        max-width: 760px;
        margin: 0 auto;
    }

    .success-banner h2 { font-size: 1.2rem; color: var(--text); margin: 0 0 0.4rem 0; }
    .success-banner p { color: var(--text-muted); margin: 0.2rem 0; font-size: 0.9rem; }

    .github-link {
        display: inline-block;
        background: var(--accent);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 7px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 0.8rem;
        font-size: 0.85rem;
    }

    .github-link:hover { background: var(--accent-strong); }

    /* ── Footer ── */
    .site-footer {
        text-align: center;
        padding: 3rem 1rem 1.5rem;
        color: var(--text-faint);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 4rem;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"


# ── Helper: API check (kept silent — no raw status shown to the user) ─────
def check_api() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def start_build(request: str, auto_push: bool, auto_open: bool, private: bool, branches: list) -> str:
    r = requests.post(f"{API_URL}/build", json={
        "request": request,
        "auto_push": auto_push,
        "auto_open_vscode": auto_open,
        "private_repo": private,
        "extra_branches": branches,
    })
    return r.json().get("build_id", "")


def get_build_events(build_id: str, since: int = 0) -> dict:
    r = requests.get(f"{API_URL}/build/{build_id}/events", params={"since": since})
    return r.json()


def get_build_status(build_id: str) -> dict:
    r = requests.get(f"{API_URL}/build/{build_id}")
    return r.json()


def list_projects() -> list:
    try:
        r = requests.get(f"{API_URL}/projects", timeout=5)
        return r.json().get("projects", [])
    except Exception:
        return []


api_ok = check_api()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">◆ Project TITAN</div>', unsafe_allow_html=True)

    with st.expander("Build options", expanded=False):
        auto_push = st.toggle("Push to GitHub", value=True)
        auto_open = st.toggle("Open in VS Code", value=True)
        private_repo = st.toggle("Private repository", value=False)
        branches_input = st.text_input("Extra branches", value="develop",
                                        help="Comma-separated branch names")
        extra_branches = [b.strip() for b in branches_input.split(",") if b.strip()]

    st.markdown("---")
    st.markdown('<div class="nav-item">Recent builds</div>', unsafe_allow_html=True)
    projects = list_projects()
    if projects:
        for p in projects[:5]:
            mark = "✓" if p["status"] == "done" else "…" if p["status"] == "building" else "✕"
            link = f" · [GitHub]({p['github_url']})" if p.get("github_url") else ""
            st.markdown(f'<div class="project-row">{mark} <strong>{p["name"]}</strong>{link}</div>', unsafe_allow_html=True)
    else:
        st.caption("Nothing built yet.")

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge"><span class="dot"></span>Now building</div>
    <h1>Describe it. TITAN builds it.</h1>
    <p>Turn a single sentence into a working, tested project — planned, written,
    and shipped to GitHub automatically.</p>
</div>
""", unsafe_allow_html=True)

# ── How it works ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="step-label">01 — PLAN</div>
        <h3>Plan</h3>
        <p>Your idea is broken into a sequence of precise, ordered build tasks.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="step-label">02 — BUILD</div>
        <h3>Build</h3>
        <p>Production files are written, tested, and fixed automatically.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="step-label">03 — SHIP</div>
        <h3>Ship</h3>
        <p>A repository is created, code is pushed, and docs are generated.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Build panel ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Start a build</div>', unsafe_allow_html=True)

_, mid, _ = st.columns([1, 4, 1])
with mid:
    st.markdown('<div class="build-panel">', unsafe_allow_html=True)

    st.markdown("**Popular templates**")
    example_cols = st.columns(4)
    examples = [
        "FastAPI Todo REST API with SQLite",
        "CLI weather app using OpenWeatherMap",
        "Flask blog with user auth",
        "Web scraper for news headlines",
    ]
    for i, (col, example) in enumerate(zip(example_cols, examples)):
        with col:
            if st.button(example, key=f"ex_{i}"):
                st.session_state["user_request"] = f"Build a {example}"

    user_request = st.text_area(
        "What do you want to build?",
        value=st.session_state.get("user_request", ""),
        placeholder="Build me a FastAPI Todo REST API with SQLite database, user authentication, and OpenAPI docs...",
        height=110,
        key="main_input",
        label_visibility="collapsed",
    )

    build_clicked = st.button("Launch build", disabled=not user_request.strip())
    st.markdown('</div>', unsafe_allow_html=True)

# ── Build Flow ────────────────────────────────────────────────────────────
if build_clicked and user_request.strip():
    if not api_ok:
        st.error("We can't start a build right now. Please try again in a moment.")
    else:
        st.session_state["build_id"] = None
        st.session_state["build_done"] = False
        st.session_state["events_seen"] = 0

        with st.spinner("Getting started..."):
            try:
                build_id = start_build(
                    request=user_request,
                    auto_push=auto_push,
                    auto_open=auto_open,
                    private=private_repo,
                    branches=extra_branches,
                )
                st.session_state["build_id"] = build_id
            except Exception:
                st.error("We can't start a build right now. Please try again in a moment.")

# ── Live Build Monitor ─────────────────────────────────────────────────────
if st.session_state.get("build_id") and not st.session_state.get("build_done"):
    build_id = st.session_state["build_id"]

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 4, 1])
    with mid:
        st.markdown('<div class="section-label">Building</div>', unsafe_allow_html=True)
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Build log**")
        log_placeholder = st.empty()

    events_seen = st.session_state.get("events_seen", 0)
    all_events = []

    while True:
        try:
            status_data = get_build_status(build_id)
            events_data = get_build_events(build_id, since=events_seen)

            new_events = events_data.get("events", [])
            all_events.extend(new_events)
            events_seen += len(new_events)
            st.session_state["events_seen"] = events_seen

            progress = status_data.get("progress", 0) / 100
            progress_placeholder.progress(progress, text=f"{int(progress * 100)}% complete")

            current_agent = status_data.get("current_agent", "titan")
            current_action = status_data.get("current_action", "Working...")
            status_placeholder.markdown(f"*{current_action}*")

            log_html = '<div class="event-log">'
            for event in reversed(all_events[-50:]):
                agent = event.get("agent", "titan")
                action = event.get("action", "")
                message = event.get("message", "")
                efile = event.get("file_path", "")
                file_part = f" <span style='color:#5B6EF5'>→ {efile}</span>" if efile else ""
                log_html += f"""
                <div class="event-line">
                    <span class="agent-badge"><span class="dot dot-{agent}"></span>{agent}</span>
                    <span style="color:var(--text)">{action}</span>
                    <span style="color:var(--text-faint)">{message[:60]}</span>
                    {file_part}
                </div>
                """
            log_html += "</div>"
            log_placeholder.markdown(log_html, unsafe_allow_html=True)

            if status_data.get("status") in ("done", "failed"):
                result = status_data.get("result", {})
                st.session_state["build_done"] = True
                st.session_state["build_result"] = result
                break

        except Exception:
            st.error("Something interrupted the build. Please try again.")
            break

        time.sleep(2)

    st.rerun()

# ── Build Result ──────────────────────────────────────────────────────────
if st.session_state.get("build_done") and st.session_state.get("build_result"):
    result = st.session_state["build_result"]
    st.markdown("<br>", unsafe_allow_html=True)

    if result.get("success"):
        st.markdown(f"""
        <div class="success-banner">
            <h2>Build complete</h2>
            <p><strong>{result.get("project_name", "")}</strong> was built successfully in {result.get("duration_seconds", 0)}s</p>
            <p>{result.get("tasks_completed", 0)} tasks completed · {len(result.get("files_created", []))} files created</p>
            {"<a class='github-link' href='" + result['github_url'] + "' target='_blank'>View on GitHub →</a>" if result.get("github_url") else ""}
        </div>
        """, unsafe_allow_html=True)

        _, mid, _ = st.columns([1, 4, 1])
        with mid:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Files created**")
                for f in result.get("files_created", []):
                    st.markdown(f"- `{f}`")
            with col_b:
                if result.get("errors"):
                    st.markdown("**Warnings**")
                    for err in result.get("errors", []):
                        st.warning(err)
                else:
                    st.success("No errors")

            if st.button("Build another project"):
                st.session_state.clear()
                st.rerun()

    else:
        _, mid, _ = st.columns([1, 4, 1])
        with mid:
            st.error("This build didn't complete. Please try again.")
            if st.button("Try again"):
                st.session_state.clear()
                st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
    Project TITAN — planned, built, and shipped by AI.
</div>
""", unsafe_allow_html=True)