"""
Project TITAN — Dashboard
Dark premium enterprise UI.
"""

import os
import sys
import time

import requests
import streamlit as st

# Allow importing complete_project from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project TITAN — AI Build Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System ──────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg:           #0A0A0F;
        --bg-2:         #0F0F18;
        --surface:      #13131E;
        --surface-2:    #1A1A2E;
        --surface-3:    #1F1F35;
        --glass:        rgba(255,255,255,0.04);
        --glass-border: rgba(255,255,255,0.08);

        --violet:       #7C3AED;
        --violet-light: #A78BFA;
        --violet-glow:  rgba(124,58,237,0.25);
        --violet-dim:   rgba(124,58,237,0.12);

        --cyan:         #06B6D4;
        --cyan-dim:     rgba(6,182,212,0.15);

        --border:       rgba(255,255,255,0.07);
        --border-mid:   rgba(255,255,255,0.12);
        --border-strong:rgba(255,255,255,0.18);

        --text:         #F1F0FF;
        --text-2:       #C4C2D4;
        --text-muted:   #7B79A0;
        --text-faint:   #4A4870;

        --success:      #22C55E;
        --success-dim:  rgba(34,197,94,0.15);
        --error:        #EF4444;
        --error-dim:    rgba(239,68,68,0.15);
        --warning:      #F59E0B;
        --warning-dim:  rgba(245,158,11,0.15);

        --radius:       14px;
        --radius-lg:    20px;
        --shadow:       0 8px 32px rgba(0,0,0,0.5);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(124,58,237,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(124,58,237,0.03) 1px, transparent 1px);
        background-size: 64px 64px;
        pointer-events: none;
        z-index: 0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

    .sb-brand {
        padding: 1.75rem 1.25rem 1.25rem;
        border-bottom: 1px solid var(--border);
        background: linear-gradient(135deg, var(--surface-2), var(--surface));
        position: relative;
        overflow: hidden;
    }
    .sb-brand::before {
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, var(--violet-glow), transparent 70%);
        pointer-events: none;
    }
    .sb-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 0.75rem; }
    .sb-logo-icon {
        width: 40px; height: 40px;
        background: linear-gradient(135deg, var(--violet), #5B21B6);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; flex-shrink: 0;
        box-shadow: 0 4px 16px var(--violet-glow);
    }
    .sb-logo-text { font-size: 1.05rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
    .sb-logo-sub { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

    .sb-status {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.7rem; color: var(--success); font-weight: 600;
        background: var(--success-dim);
        border: 1px solid rgba(34,197,94,0.2);
        padding: 4px 10px; border-radius: 100px; letter-spacing: 0.02em;
    }
    .sb-status .pulse {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--success);
        animation: pulse 2s ease-in-out infinite; flex-shrink: 0;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }
    .sb-status.offline { color: var(--error); background: var(--error-dim); border-color: rgba(239,68,68,0.2); }
    .sb-status.offline .pulse { background: var(--error); animation: none; }

    .sb-section-title {
        font-size: 0.6rem; font-weight: 700; letter-spacing: 0.14em;
        text-transform: uppercase; color: var(--text-faint);
        padding: 1.1rem 1.25rem 0.4rem;
    }
    .sb-option-row { padding: 0.1rem 1rem; }
    .sb-divider { border: none; border-top: 1px solid var(--border); margin: 0.75rem 1rem; }

    .sb-project-item {
        display: flex; align-items: center; gap: 9px;
        padding: 0.55rem 1.25rem; font-size: 0.8rem;
        color: var(--text-2); cursor: default; transition: background 0.15s;
    }
    .sb-project-item:hover { background: var(--glass); }
    .sb-project-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .sb-project-name {
        flex: 1; overflow: hidden; text-overflow: ellipsis;
        white-space: nowrap; font-weight: 500; font-size: 0.8rem;
    }
    .sb-project-link {
        font-size: 0.67rem; color: var(--violet-light); font-weight: 600;
        text-decoration: none; flex-shrink: 0;
        padding: 2px 8px; border-radius: 5px;
        background: var(--violet-dim); border: 1px solid rgba(124,58,237,0.2);
        transition: all 0.15s;
    }
    .sb-project-link:hover { background: var(--violet-glow); color: white; text-decoration: none; }
    .sb-empty { padding: 0.6rem 1.25rem; font-size: 0.78rem; color: var(--text-faint); font-style: italic; }

    [data-testid="stToggle"] > label { color: var(--text-2) !important; font-size: 0.84rem !important; font-weight: 500 !important; }

    /* Main */
    .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }

    .page-header {
        background: linear-gradient(135deg, var(--surface-2), var(--bg-2));
        border-bottom: 1px solid var(--border);
        padding: 1.5rem 2.5rem;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 2.5rem;
        position: relative; overflow: hidden;
    }
    .page-header::after {
        content: '';
        position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, var(--violet), var(--cyan), transparent);
    }
    .header-brand { display: flex; align-items: center; gap: 16px; }
    .header-icon {
        width: 52px; height: 52px;
        background: linear-gradient(135deg, var(--violet), #4F46E5);
        border-radius: 14px; display: flex; align-items: center; justify-content: center;
        font-size: 24px; box-shadow: 0 8px 24px var(--violet-glow);
    }
    .header-title {
        font-size: 1.6rem; font-weight: 900; letter-spacing: -0.04em;
        background: linear-gradient(135deg, #F1F0FF, var(--violet-light));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; line-height: 1.1;
    }
    .header-sub { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }
    .header-meta { display: flex; align-items: center; gap: 10px; }
    .header-badge {
        font-size: 0.67rem; font-weight: 700; letter-spacing: 0.08em;
        text-transform: uppercase; color: var(--violet-light);
        background: var(--violet-dim); border: 1px solid rgba(124,58,237,0.25);
        padding: 4px 10px; border-radius: 100px;
    }
    .api-badge-ok {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.7rem; font-weight: 600; color: var(--success);
        background: var(--success-dim); border: 1px solid rgba(34,197,94,0.2);
        padding: 5px 12px; border-radius: 100px;
    }
    .api-badge-err {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.7rem; font-weight: 600; color: var(--error);
        background: var(--error-dim); border: 1px solid rgba(239,68,68,0.2);
        padding: 5px 12px; border-radius: 100px;
    }
    .dot-sm { width: 6px; height: 6px; border-radius: 50%; animation: pulse 2s infinite; }

    /* Feature cards */
    .stat-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 1.5rem;
        position: relative; overflow: hidden;
        transition: border-color 0.2s, transform 0.2s;
    }
    .stat-card:hover { border-color: var(--border-mid); transform: translateY(-3px); }
    .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
    .stat-card.plan::before { background: linear-gradient(90deg, var(--violet), #4F46E5); }
    .stat-card.build::before { background: linear-gradient(90deg, var(--cyan), #0891B2); }
    .stat-card.ship::before { background: linear-gradient(90deg, var(--success), #15803D); }
    .stat-step { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-faint); margin-bottom: 0.75rem; }
    .stat-icon { font-size: 1.8rem; margin-bottom: 0.6rem; display: block; }
    .stat-title { font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem; letter-spacing: -0.01em; }
    .stat-desc { font-size: 0.78rem; color: var(--text-muted); line-height: 1.55; }

    /* Build input card */
    .build-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 2rem 2.25rem 1.5rem;
        box-shadow: var(--shadow); margin-bottom: 1.5rem;
        position: relative; overflow: hidden;
    }
    .build-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, var(--violet), var(--cyan), var(--violet));
        background-size: 200% 100%;
        animation: shimmer 4s linear infinite;
    }
    @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    .build-card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 1.5rem; }
    .build-card-icon {
        width: 42px; height: 42px;
        background: linear-gradient(135deg, var(--violet-dim), var(--cyan-dim));
        border: 1px solid var(--border-mid); border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 19px; flex-shrink: 0;
    }
    .build-card-title { font-size: 1.1rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
    .build-card-sub { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; line-height: 1.4; }

    .quick-picks-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-faint); margin-bottom: 0.6rem; }

    /* Inputs */
    .stTextArea textarea {
        background: var(--surface-2) !important; border: 1.5px solid var(--border) !important;
        border-radius: 12px !important; color: var(--text) !important;
        font-family: 'Inter', sans-serif !important; font-size: 0.93rem !important;
        line-height: 1.6 !important; transition: border-color 0.2s, box-shadow 0.2s !important;
        caret-color: var(--violet-light) !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--violet) !important;
        box-shadow: 0 0 0 3px var(--violet-dim), 0 0 20px var(--violet-glow) !important;
        background: var(--surface-3) !important;
    }
    .stTextArea textarea::placeholder { color: var(--text-faint) !important; }

    label[data-testid="stWidgetLabel"] { font-size: 0.8rem !important; font-weight: 600 !important; color: var(--text-2) !important; }

    .stTextInput input {
        background: var(--surface-2) !important; border: 1.5px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important;
        font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important;
    }
    .stTextInput input:focus { border-color: var(--violet) !important; box-shadow: 0 0 0 3px var(--violet-dim) !important; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--violet), #4F46E5) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 0.9rem !important; padding: 0.7rem 1.75rem !important;
        transition: all 0.2s ease !important; box-shadow: 0 4px 20px var(--violet-glow) !important;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 32px var(--violet-glow), 0 0 24px rgba(124,58,237,0.4) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }
    .stButton > button:disabled { background: var(--surface-3) !important; color: var(--text-faint) !important; box-shadow: none !important; transform: none !important; }

    /* Monitor */
    .monitor-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 2rem; box-shadow: var(--shadow);
        margin-bottom: 1.25rem; position: relative; overflow: hidden;
    }
    .monitor-card::before {
        content: ''; position: absolute; inset: 0;
        background: radial-gradient(ellipse at 80% 0%, var(--violet-dim), transparent 60%);
        pointer-events: none;
    }
    .monitor-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
    .monitor-title { font-size: 1rem; font-weight: 700; color: var(--text); letter-spacing: -0.02em; display: flex; align-items: center; gap: 10px; }
    .monitor-spinner {
        width: 14px; height: 14px; border: 2px solid var(--border-mid);
        border-top-color: var(--violet-light); border-radius: 50%;
        animation: spin 0.8s linear infinite; display: inline-block;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .monitor-pct {
        font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; font-weight: 700;
        color: var(--violet-light); background: var(--violet-dim);
        border: 1px solid rgba(124,58,237,0.25); padding: 4px 14px; border-radius: 100px;
    }
    .stProgress > div > div { background: linear-gradient(90deg, var(--violet), var(--cyan)) !important; border-radius: 100px !important; }
    .stProgress > div { background: var(--surface-3) !important; border-radius: 100px !important; height: 6px !important; }

    .agent-badge {
        display: inline-flex; align-items: center; gap: 5px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.67rem; font-weight: 700;
        letter-spacing: 0.06em; text-transform: uppercase;
        color: var(--violet-light); background: var(--violet-dim);
        border: 1px solid rgba(124,58,237,0.2); padding: 3px 9px; border-radius: 5px; margin-right: 8px;
    }

    /* Log */
    .log-wrap {
        background: var(--bg-2); border: 1px solid var(--border); border-radius: 12px;
        padding: 0.25rem 0; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
        max-height: 360px; overflow-y: auto;
    }
    .log-line { display: flex; align-items: center; gap: 10px; padding: 7px 14px; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.1s; }
    .log-line:hover { background: var(--glass); }
    .log-line:last-child { border-bottom: none; }
    .log-agent {
        display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px;
        border-radius: 5px; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.05em;
        text-transform: uppercase; background: var(--glass); border: 1px solid var(--border);
        color: var(--text-muted); flex-shrink: 0; min-width: 82px; justify-content: center;
    }
    .agent-dot { width: 5px; height: 5px; border-radius: 50%; display: inline-block; }
    .dot-planner    { background: #818CF8; }
    .dot-code       { background: #22C55E; }
    .dot-testing    { background: #F59E0B; }
    .dot-docs       { background: #C084FC; }
    .dot-github     { background: #7C3AED; }
    .dot-filesystem { background: #06B6D4; }
    .dot-terminal   { background: #EF4444; }
    .dot-titan      { background: #4A4870; }
    .dot-vscode     { background: #3B82F6; }
    .log-action { flex: 1; color: var(--text-2); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .log-file { color: var(--cyan); font-size: 0.7rem; flex-shrink: 0; }

    /* Result */
    .result-card {
        background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 2rem 2.25rem;
        box-shadow: var(--shadow); margin-bottom: 1.5rem;
        position: relative; overflow: hidden;
    }
    .result-card.success { border-color: rgba(34,197,94,0.25); box-shadow: 0 0 40px rgba(34,197,94,0.08), var(--shadow); }
    .result-card.success::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--success), var(--cyan)); }
    .result-card.error { border-color: rgba(239,68,68,0.25); }
    .result-card.error::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--error); }
    .result-title { font-size: 1.25rem; font-weight: 900; color: var(--text); letter-spacing: -0.03em; margin-bottom: 0.25rem; }
    .result-meta { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1.25rem; font-family: 'JetBrains Mono', monospace; }
    .stat-pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.5rem; }
    .stat-pill { display: inline-flex; align-items: center; gap: 5px; padding: 5px 13px; border-radius: 100px; font-size: 0.77rem; font-weight: 600; background: var(--glass); border: 1px solid var(--border-mid); color: var(--text-2); }

    .gh-btn {
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, var(--violet), #4F46E5);
        color: white !important; text-decoration: none !important;
        padding: 0.6rem 1.4rem; border-radius: 10px;
        font-size: 0.85rem; font-weight: 700; letter-spacing: -0.01em;
        box-shadow: 0 4px 20px var(--violet-glow); transition: all 0.2s ease;
    }
    .gh-btn:hover { box-shadow: 0 8px 32px var(--violet-glow), 0 0 24px rgba(124,58,237,0.4); transform: translateY(-2px); color: white !important; text-decoration: none !important; }

    .file-list { background: var(--bg-2); border: 1px solid var(--border); border-radius: 10px; padding: 0.5rem; max-height: 260px; overflow-y: auto; }
    .file-item { display: flex; align-items: center; gap: 8px; padding: 5px 10px; border-radius: 6px; font-size: 0.75rem; color: var(--text-2); font-family: 'JetBrains Mono', monospace; transition: background 0.1s; }
    .file-item:hover { background: var(--glass); }

    .stAlert { border-radius: 10px !important; }

    .stExpander details { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--surface) !important; }
    .stExpander summary { font-size: 0.85rem !important; font-weight: 600 !important; color: var(--text-2) !important; }

    hr { border-color: var(--border) !important; }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 100px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

    .titan-footer { text-align: center; padding: 2.5rem 0 1.5rem; border-top: 1px solid var(--border); margin-top: 4rem; color: var(--text-faint); font-size: 0.73rem; }
    .titan-footer span { font-family: 'JetBrains Mono', monospace; color: var(--text-muted); }
    .titan-footer a { color: var(--violet-light); text-decoration: none; }
    .titan-footer a:hover { text-decoration: underline; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Constants ──────────────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000"

QUICK_PICKS = [
    ("🚀", "FastAPI REST API"),
    ("🌐", "React + Node web app"),
    ("🤖", "Python CLI tool"),
    ("📊", "Flask dashboard"),
    ("🔐", "Auth microservice"),
    ("🕷️", "Web scraper"),
]


# ── Helpers ────────────────────────────────────────────────────────────────
def check_api() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def start_build(request: str, auto_push: bool, auto_open: bool, private: bool, branches: list) -> str:
    r = requests.post(
        f"{API_URL}/build",
        json={"request": request, "auto_push": auto_push, "auto_open_vscode": auto_open, "private_repo": private, "extra_branches": branches},
        timeout=10,
    )
    return r.json().get("build_id", "")


def get_build_events(build_id: str, since: int = 0) -> dict:
    r = requests.get(f"{API_URL}/build/{build_id}/events", params={"since": since}, timeout=5)
    return r.json()


def get_build_status(build_id: str) -> dict:
    r = requests.get(f"{API_URL}/build/{build_id}", timeout=5)
    return r.json()


def list_projects() -> list:
    try:
        r = requests.get(f"{API_URL}/projects", timeout=5)
        return r.json().get("projects", [])
    except Exception:
        return []


# ── Init session ───────────────────────────────────────────────────────────
for key in ("build_id", "build_done", "build_result", "events_seen", "user_request"):
    if key not in st.session_state:
        st.session_state[key] = None if key != "events_seen" else 0

api_ok = check_api()

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    status_class = "sb-status" if api_ok else "sb-status offline"
    status_text = "System online" if api_ok else "Backend offline"
    st.markdown(
        f"""
<div class="sb-brand">
    <div class="sb-logo">
        <div class="sb-logo-icon">⚡</div>
        <div>
            <div class="sb-logo-text">Project TITAN</div>
            <div class="sb-logo-sub">AI Build Engine</div>
        </div>
    </div>
    <div class="{status_class}">
        <span class="pulse"></span>{status_text}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section-title">Build Options</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sb-option-row">', unsafe_allow_html=True)
        auto_push = st.toggle("Push to GitHub", value=True)
        auto_open = st.toggle("Open in VS Code", value=True)
        private_repo = st.toggle("Private repository", value=False)
        branches_input = st.text_input("Extra branches", value="develop", help="Comma-separated branch names")
        extra_branches = [b.strip() for b in branches_input.split(",") if b.strip()]
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-section-title">Recent Builds</div>', unsafe_allow_html=True)
    projects = list_projects()
    if projects:
        for p in projects[:8]:
            color = "#22C55E" if p["status"] == "done" else "#F59E0B" if p["status"] == "building" else "#EF4444"
            gh_link = f'<a class="sb-project-link" href="{p["github_url"]}" target="_blank">GitHub ↗</a>' if p.get("github_url") else ""
            st.markdown(
                f"""
<div class="sb-project-item">
    <span class="sb-project-dot" style="background:{color}"></span>
    <span class="sb-project-name">{p['name']}</span>
    {gh_link}
</div>
""",
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="sb-empty">No builds yet</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════
_, col_main, _ = st.columns([0.3, 10, 0.3])
with col_main:

    # Header
    api_badge = (
        '<div class="api-badge-ok"><span class="dot-sm" style="background:#22C55E"></span>API Connected</div>'
        if api_ok
        else '<div class="api-badge-err"><span class="dot-sm" style="background:#EF4444"></span>API Offline</div>'
    )
    st.markdown(
        f"""
<div class="page-header">
    <div class="header-brand">
        <div class="header-icon">⚡</div>
        <div>
            <div class="header-title">Build Dashboard</div>
            <div class="header-sub">Autonomous AI software engineering at scale</div>
        </div>
    </div>
    <div class="header-meta">
        <span class="header-badge">v1.0</span>
        {api_badge}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Feature cards
    c1, c2, c3 = st.columns(3)
    cards = [
        ("01 — PLAN", "plan", "🧠", "Intelligent Planning", "Decomposes your idea into a precise, ordered sequence of build tasks."),
        ("02 — BUILD", "build", "⚙️", "Autonomous Coding", "AI agents write, test, and fix all files — end-to-end, zero intervention."),
        ("03 — SHIP", "ship", "🚀", "Auto Deploy", "Repository created, code pushed, README and CI/CD written automatically."),
    ]
    for col, (step, cls, emoji, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(
                f"""
<div class="stat-card {cls}">
    <div class="stat-step">{step}</div>
    <span class="stat-icon">{emoji}</span>
    <div class="stat-title">{title}</div>
    <div class="stat-desc">{desc}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Build input
    st.markdown(
        """
<div class="build-card">
    <div class="build-card-header">
        <div class="build-card-icon">✍️</div>
        <div>
            <div class="build-card-title">Describe your project</div>
            <div class="build-card-sub">TITAN will plan, code, test, and ship it automatically — no intervention required</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="quick-picks-label">Quick picks</div>', unsafe_allow_html=True)
    qp_cols = st.columns(len(QUICK_PICKS))
    for i, (col, (emoji, label)) in enumerate(zip(qp_cols, QUICK_PICKS)):
        with col:
            if st.button(f"{emoji} {label}", key=f"qp_{i}", use_container_width=True):
                st.session_state["user_request"] = f"Build a {label}"
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    user_request = st.text_area(
        "Project description",
        value=st.session_state.get("user_request") or "",
        placeholder="e.g.  Build a FastAPI Todo REST API with SQLite, JWT auth, and auto-generated OpenAPI docs…",
        height=130,
        key="main_input",
    )
    st.session_state["user_request"] = user_request

    launch_col, _ = st.columns([2, 5])
    with launch_col:
        build_clicked = st.button("⚡  Launch TITAN", disabled=not user_request.strip(), use_container_width=True)

    if not api_ok:
        st.warning("⚠️  Backend is offline. Start it with `python -m backend.main`.", icon=None)

    if build_clicked and user_request.strip():
        if not api_ok:
            st.error("⚠️ Backend is offline — start it with `python -m backend.main`.")
        else:
            st.session_state.update({"build_id": None, "build_done": False, "build_result": None, "events_seen": 0})
            try:
                build_id = start_build(request=user_request, auto_push=auto_push, auto_open=auto_open, private=private_repo, branches=extra_branches)
                st.session_state["build_id"] = build_id
            except Exception as e:
                st.error(f"Could not start build: {e}")

    # Live monitor
    if st.session_state.get("build_id") and not st.session_state.get("build_done"):
        build_id = st.session_state["build_id"]
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        progress_placeholder = st.empty()
        log_placeholder = st.empty()
        events_seen = st.session_state.get("events_seen", 0)
        all_events: list = []

        while True:
            try:
                status_data = get_build_status(build_id)
                events_data = get_build_events(build_id, since=events_seen)
                new_events = events_data.get("events", [])
                all_events.extend(new_events)
                events_seen += len(new_events)
                st.session_state["events_seen"] = events_seen

                pct = int(status_data.get("progress", 0))
                current_action = status_data.get("current_action", "Working…")
                current_agent = status_data.get("current_agent", "titan")

                with progress_placeholder.container():
                    st.markdown(
                        f"""
<div class="monitor-card">
    <div class="monitor-header">
        <div class="monitor-title">
            <span class="monitor-spinner"></span>
            Building your project…
        </div>
        <div class="monitor-pct">{pct}%</div>
    </div>
""",
                        unsafe_allow_html=True,
                    )
                    st.progress(pct / 100)
                    st.markdown(
                        f"""
    <div style="margin-top:0.9rem;font-size:0.82rem;color:var(--text-muted);">
        <span class="agent-badge">{current_agent}</span>{current_action}
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                log_rows = ""
                for event in reversed(all_events[-60:]):
                    agent = event.get("agent", "titan")
                    action = event.get("action", "")
                    msg = event.get("message", "")
                    efile = event.get("file_path", "")
                    file_badge = f'<span class="log-file">→ {efile}</span>' if efile else ""
                    short_msg = (msg[:55] + "…") if len(msg) > 55 else msg
                    log_rows += f"""
<div class="log-line">
    <span class="log-agent"><span class="agent-dot dot-{agent}"></span>{agent}</span>
    <span class="log-action">{action} <span style="color:var(--text-faint);font-weight:400">{short_msg}</span></span>
    {file_badge}
</div>"""

                _empty_log = '<div class="log-line" style="color:var(--text-faint)">Waiting for first event…</div>'
                log_placeholder.markdown(
                    f'<div class="log-wrap">{log_rows or _empty_log}</div>',
                    unsafe_allow_html=True,
                )

                if status_data.get("status") in ("done", "failed"):
                    st.session_state["build_done"] = True
                    st.session_state["build_result"] = status_data.get("result", {})
                    break

            except Exception as e:
                st.session_state.update({"build_done": True, "build_result": {"success": False, "error": str(e)}})
                break

            time.sleep(2)
        st.rerun()

    # Result
    if st.session_state.get("build_done") and st.session_state.get("build_result"):
        result = st.session_state["build_result"]
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        if result.get("success"):
            files = result.get("files_created", [])
            duration = result.get("duration_seconds", 0)
            tasks = result.get("tasks_completed", 0)
            gh_url = result.get("github_url", "")
            gh_btn = f'<a class="gh-btn" href="{gh_url}" target="_blank">⬡ View on GitHub</a>' if gh_url else ""
            gh_pill = "<span class='stat-pill' style='color:var(--success);border-color:rgba(34,197,94,0.25)'>✓ Pushed to GitHub</span>" if gh_url else ""

            html_parts = [
                f'<div class="result-title">✅ Build Complete — {result.get("project_name", "Project")}</div>',
                f'<div class="result-meta">Finished in {duration:.1f}s</div>',
                '<div class="stat-pills">',
                f'<span class="stat-pill">📋 {tasks} tasks</span>',
                f'<span class="stat-pill">📁 {len(files)} files</span>'
            ]
            if private_repo:
                html_parts.append("<span class='stat-pill'>🔒 Private</span>")
            if gh_url:
                html_parts.append("<span class='stat-pill' style='color:var(--success);border-color:rgba(34,197,94,0.25)'>✓ Pushed to GitHub</span>")
            html_parts.append("</div>")
            if gh_url:
                html_parts.append(f'<a class="gh-btn" href="{gh_url}" target="_blank">⬡ View on GitHub</a>')
                
            inner_html = "".join(html_parts)
            
            st.markdown(
                f'<div class="result-card success">{inner_html}</div>',
                unsafe_allow_html=True,
            )

            if files:
                col_files, col_warn = st.columns([3, 2])
                with col_files:
                    st.markdown('<div style="font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.6rem;letter-spacing:0.1em;text-transform:uppercase;">Files Created</div>', unsafe_allow_html=True)
                    file_rows = "".join(f'<div class="file-item"><span style="color:var(--cyan)">◈</span> {f}</div>' for f in files)
                    st.markdown(f'<div class="file-list">{file_rows}</div>', unsafe_allow_html=True)
                with col_warn:
                    errors = result.get("errors", [])
                    if errors:
                        st.markdown('<div style="font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.6rem;letter-spacing:0.1em;text-transform:uppercase;">Warnings</div>', unsafe_allow_html=True)
                        for err in errors:
                            st.warning(err)
                    else:
                        st.markdown('<div style="font-size:0.8rem;font-weight:700;color:var(--success);margin-top:0.5rem;">✓ No warnings</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # ── Post-build automation: screenshots + GitHub push + LinkedIn ──
            st.markdown("""
<div style='background:linear-gradient(135deg,#1A1A2E,#13131E);
            border:1px solid rgba(124,58,237,0.3);
            border-radius:14px;padding:1.5rem 2rem;margin:1rem 0;'>
  <div style='font-size:1rem;font-weight:700;color:#A78BFA;margin-bottom:0.5rem;'>📸 Project Completion Snapshot</div>
  <div style='font-size:0.82rem;color:#7B79A0;'>Taking screenshots & posting to LinkedIn automatically…</div>
</div>""", unsafe_allow_html=True)

            with st.spinner("🎨 Generating project card & posting to LinkedIn…"):
                try:
                    import complete_project
                    import importlib
                    importlib.reload(complete_project)  # pick up any code changes
                    gh_url = result.get("github_url", "https://github.com/HarshS99/Project_TITAN")
                    project_nm  = result.get("project_name", "My Project")
                    project_desc = result.get("project_description", "")
                    tech_stack   = result.get("tech_stack", [])
                    num_files    = len(result.get("files_created", []))
                    num_tasks    = result.get("total_tasks", 0)
                    comp = complete_project.run(
                        project_name=project_nm,
                        description=project_desc,
                        tech_stack=tech_stack,
                        github_url=gh_url,
                        num_files=num_files,
                        num_tasks=num_tasks,
                    )
                except Exception as e:
                    comp = {"errors": [str(e)], "vscode_screenshot": None,
                            "github_screenshot": None, "linkedin_post_url": None,
                            "project_card": None}

            ss_col1, ss_col2 = st.columns(2)
            card_path = comp.get("project_card")
            with ss_col1:
                if card_path and os.path.exists(card_path):
                    st.image(card_path, caption="🎨 Project Card — LinkedIn Cover", use_container_width=True)
                else:
                    st.info("Project card unavailable")
            with ss_col2:
                if card_path and os.path.exists(card_path):
                    st.image(card_path, caption="🚀 Built 100% by AI — Project TITAN", use_container_width=True)
                else:
                    st.info("Project card unavailable")

            # LinkedIn result
            li_url = comp.get("linkedin_post_url")
            if li_url:
                st.markdown(f"""
<div style='background:linear-gradient(135deg,#0d3349,#0a2233);
            border:1px solid rgba(0,119,181,0.4);
            border-radius:12px;padding:1.2rem 1.8rem;margin:1rem 0;text-align:center;'>
  <div style='font-size:1rem;font-weight:700;color:#00A0DC;margin-bottom:0.5rem;'>🔗 LinkedIn Post Published!</div>
  <a href='{li_url}' target='_blank'
     style='color:#7dd3fc;font-size:0.85rem;font-weight:600;word-break:break-all;'>{li_url}</a>
</div>""", unsafe_allow_html=True)
            else:
                if not (os.getenv("LINKEDIN_ACCESS_TOKEN", "your_linkedin_token_here") == "your_linkedin_token_here"):
                    errs = comp.get("errors", [])
                    li_err = next((e for e in errs if "LinkedIn" in e or "linkedin" in e), None)
                    if li_err:
                        st.warning(f"LinkedIn: {li_err}")

            # Git push status
            if comp.get("github_pushed"):
                st.success("✅ Code pushed to GitHub!")

            # Non-critical errors
            other_errs = [e for e in comp.get("errors", []) if "LinkedIn" not in e]
            for err in other_errs:
                st.warning(err)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            if st.button("⚡  Build another project"):
                st.session_state.clear()
                st.rerun()
        else:
            st.markdown(
                """
<div class="result-card error">
    <div class="result-title">❌ Build Failed</div>
    <div class="result-meta">Something went wrong during the build. Check the log above for details.</div>
</div>
""",
                unsafe_allow_html=True,
            )
            if st.button("↩ Try again"):
                st.session_state.clear()
                st.rerun()

    # Footer
    st.markdown(
        """
<div class="titan-footer">
    Project TITAN &nbsp;·&nbsp; Planned, coded &amp; shipped by AI &nbsp;·&nbsp;
    <span>v1.0.0</span>
    &nbsp;·&nbsp;
    <a href="https://github.com/HarshS99/Project_TITAN" target="_blank">GitHub ↗</a>
</div>
""",
        unsafe_allow_html=True,
    )
