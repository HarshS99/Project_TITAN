"""
Project TITAN — Autonomous AI Software Engineering Console
Ultra-modern dark enterprise UI with real-time agent telemetry,
multi-page operations, dynamic color theme engine, and floating AI Copilot chatbot.
"""

from __future__ import annotations

import io
import os
import sys
import time
import zipfile
from pathlib import Path

import requests
import streamlit as st

# Ensure backend modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Color Theme Palettes ───────────────────────────────────────────────────
THEMES = {
    "Cyber Emerald (Ops Console)": {
        "primary": "#10B981",
        "primary_glow": "rgba(16, 185, 129, 0.4)",
        "primary_dim": "rgba(16, 185, 129, 0.14)",
        "primary_light": "#34D399",
        "accent": "#06B6D4",
        "accent_glow": "rgba(6, 182, 212, 0.4)",
        "bg": "#04080D",
        "bg_alt": "#081018",
        "surface": "#0D1826",
        "surface_2": "#132337",
        "surface_3": "#1A304B",
        "border": "rgba(16, 185, 129, 0.2)",
        "border_hover": "rgba(16, 185, 129, 0.55)",
        "gradient": "linear-gradient(135deg, #10B981 0%, #059669 45%, #06B6D4 100%)",
        "logo_gradient": "linear-gradient(135deg, #10B981, #047857)",
        "text": "#F0FDF4",
    },
    "Electric Cyan (Sci-Fi Matrix)": {
        "primary": "#06B6D4",
        "primary_glow": "rgba(6, 182, 212, 0.4)",
        "primary_dim": "rgba(6, 182, 212, 0.14)",
        "primary_light": "#67E8F9",
        "accent": "#3B82F6",
        "accent_glow": "rgba(59, 130, 246, 0.4)",
        "bg": "#030712",
        "bg_alt": "#070E1E",
        "surface": "#0C162E",
        "surface_2": "#132142",
        "surface_3": "#1B2F5C",
        "border": "rgba(6, 182, 212, 0.2)",
        "border_hover": "rgba(6, 182, 212, 0.55)",
        "gradient": "linear-gradient(135deg, #06B6D4 0%, #2563EB 50%, #3B82F6 100%)",
        "logo_gradient": "linear-gradient(135deg, #06B6D4, #1D4ED8)",
        "text": "#F0F9FF",
    },
    "Neon Violet (Synthwave Nebula)": {
        "primary": "#8B5CF6",
        "primary_glow": "rgba(139, 92, 246, 0.4)",
        "primary_dim": "rgba(139, 92, 246, 0.14)",
        "primary_light": "#C4B5FD",
        "accent": "#EC4899",
        "accent_glow": "rgba(236, 72, 153, 0.4)",
        "bg": "#080612",
        "bg_alt": "#0F0B20",
        "surface": "#16122F",
        "surface_2": "#1E1940",
        "surface_3": "#2B245A",
        "border": "rgba(139, 92, 246, 0.2)",
        "border_hover": "rgba(139, 92, 246, 0.55)",
        "gradient": "linear-gradient(135deg, #8B5CF6 0%, #7C3AED 50%, #EC4899 100%)",
        "logo_gradient": "linear-gradient(135deg, #8B5CF6, #6D28D9)",
        "text": "#F5F3FF",
    },
    "Solar Gold (Titan Amber)": {
        "primary": "#F59E0B",
        "primary_glow": "rgba(245, 158, 11, 0.4)",
        "primary_dim": "rgba(245, 158, 11, 0.14)",
        "primary_light": "#FCD34D",
        "accent": "#EF4444",
        "accent_glow": "rgba(239, 68, 68, 0.4)",
        "bg": "#0B0803",
        "bg_alt": "#140E06",
        "surface": "#1C1409",
        "surface_2": "#281D0E",
        "surface_3": "#382914",
        "border": "rgba(245, 158, 11, 0.2)",
        "border_hover": "rgba(245, 158, 11, 0.55)",
        "gradient": "linear-gradient(135deg, #F59E0B 0%, #D97706 50%, #EF4444 100%)",
        "logo_gradient": "linear-gradient(135deg, #F59E0B, #B45309)",
        "text": "#FFFBEB",
    },
    "Crimson Blood (Titan Red)": {
        "primary": "#EF4444",
        "primary_glow": "rgba(239, 68, 68, 0.4)",
        "primary_dim": "rgba(239, 68, 68, 0.14)",
        "primary_light": "#FCA5A5",
        "accent": "#F59E0B",
        "accent_glow": "rgba(245, 158, 11, 0.4)",
        "bg": "#0B0404",
        "bg_alt": "#150808",
        "surface": "#1F0D0D",
        "surface_2": "#2C1313",
        "surface_3": "#3F1B1B",
        "border": "rgba(239, 68, 68, 0.22)",
        "border_hover": "rgba(239, 68, 68, 0.55)",
        "gradient": "linear-gradient(135deg, #EF4444 0%, #DC2626 50%, #F59E0B 100%)",
        "logo_gradient": "linear-gradient(135deg, #EF4444, #991B1B)",
        "text": "#FEF2F2",
    },
}

# ── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project TITAN — Autonomous AI Build Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme_palette" not in st.session_state:
    st.session_state["theme_palette"] = "Cyber Emerald (Ops Console)"

active_theme_key = st.session_state.get("theme_palette", "Cyber Emerald (Ops Console)")
th = THEMES.get(active_theme_key, THEMES["Cyber Emerald (Ops Console)"])

# ── Dynamic Theme CSS Injection ────────────────────────────────────────────
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {{
        --bg:            {th['bg']};
        --bg-alt:        {th['bg_alt']};
        --surface:       {th['surface']};
        --surface-2:     {th['surface_2']};
        --surface-3:     {th['surface_3']};
        --glass:         rgba(255, 255, 255, 0.035);
        --glass-border:  rgba(255, 255, 255, 0.08);

        --primary:       {th['primary']};
        --primary-glow:  {th['primary_glow']};
        --primary-dim:   {th['primary_dim']};
        --primary-light: {th['primary_light']};

        --accent:        {th['accent']};
        --accent-glow:   {th['accent_glow']};

        --emerald:       #10B981;
        --emerald-dim:   rgba(16, 185, 129, 0.14);
        --amber:         #F59E0B;
        --rose:          #F43F5E;

        --border:        {th['border']};
        --border-hover:  {th['border_hover']};
        --text:          {th['text']};
        --text-2:        #C5C4DB;
        --text-muted:    #8280A3;
        --text-faint:    #4D4B70;

        --radius-sm:     8px;
        --radius:        14px;
        --radius-lg:     20px;
    }}

    /* Core Background & Layout */
    .stApp {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(circle at 15% 15%, {th['primary_dim']} 0%, transparent 45%),
            radial-gradient(circle at 85% 85%, {th['accent_glow']} 0%, transparent 45%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px;
        pointer-events: none;
        z-index: 0;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}

    /* Suppress any default full-width Streamlit bottom container */
    div[data-testid="stBottom"], div[data-testid="stChatInput"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }}

    /* ── Floating Chatbot Launcher Button (Bottom-Right Corner) ────── */
    div.st-key-titan_chat_launcher {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        left: auto !important;
        top: auto !important;
        width: 66px !important;
        height: 66px !important;
        z-index: 9999 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    div.st-key-titan_chat_launcher > button {{
        width: 66px !important;
        height: 66px !important;
        min-width: 66px !important;
        min-height: 66px !important;
        max-width: 66px !important;
        max-height: 66px !important;
        border-radius: 50% !important;
        background: #0b1620 !important;
        border: 2.5px solid #4cc38a !important;
        box-shadow: 0 8px 30px rgba(76, 195, 138, 0.5), 0 0 20px rgba(58, 168, 200, 0.3) !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease, border-color 0.2s ease !important;
    }}

    div.st-key-titan_chat_launcher > button:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 14px 40px rgba(76, 195, 138, 0.7), 0 0 30px rgba(58, 168, 200, 0.5) !important;
        border-color: #3aa8c8 !important;
    }}

    /* Big Inner ⚡ logo inside rounded green square */
    div.st-key-titan_chat_launcher > button p {{
        width: 46px !important;
        height: 46px !important;
        border-radius: 14px !important;
        background: linear-gradient(135deg, #4cc38a 0%, #3aa8c8 100%) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 28px !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(76, 195, 138, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }}

    /* Small green online dot at top-right of launcher */
    div.st-key-titan_chat_launcher::after {{
        content: '' !important;
        position: absolute !important;
        top: 2px !important;
        right: 2px !important;
        width: 14px !important;
        height: 14px !important;
        border-radius: 50% !important;
        background: #10B981 !important;
        border: 2.5px solid #0b1620 !important;
        box-shadow: 0 0 10px #10B981 !important;
        pointer-events: none !important;
        z-index: 10000 !important;
    }}

    /* ── Floating Chat Window (Anchored Above Launcher) ─────────────── */
    @keyframes titanChatSlideUp {{
        from {{
            opacity: 0;
            transform: translateY(16px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    div.st-key-titan_chat_window {{
        position: fixed !important;
        bottom: 96px !important;
        right: 24px !important;
        left: auto !important;
        top: auto !important;
        width: 380px !important;
        height: 520px !important;
        max-height: 75vh !important;
        background: #0b1620 !important;
        border: 1px solid rgba(76, 195, 138, 0.4) !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(76, 195, 138, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        z-index: 9999 !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        animation: titanChatSlideUp 0.2s ease-out !important;
        padding: 0 !important;
    }}

    /* Header close button */
    div.st-key-titan_chat_close_btn > button {{
        background: transparent !important;
        border: none !important;
        color: var(--text-muted) !important;
        font-size: 1.15rem !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: 28px !important;
        width: 28px !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div.st-key-titan_chat_close_btn > button:hover {{
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.1) !important;
        transform: none !important;
    }}

    /* Chat footer form styling inside window */
    div.st-key-titan_chat_window form {{
        border: none !important;
        padding: 8px 12px 10px !important;
        background: #08121C !important;
        border-top: 1px solid rgba(76, 195, 138, 0.2) !important;
        margin: 0 !important;
    }}

    div.st-key-titan_chat_window form [data-testid="stTextInput"] {{
        margin-bottom: 0 !important;
    }}

    div.st-key-titan_chat_window form [data-testid="stTextInput"] input {{
        background: #0D1A26 !important;
        border: 1px solid rgba(76, 195, 138, 0.3) !important;
        border-radius: 8px !important;
        color: #F0FDF4 !important;
        font-size: 0.85rem !important;
        padding: 8px 12px !important;
    }}

    div.st-key-titan_chat_window form [data-testid="stTextInput"] input:focus {{
        border-color: #4cc38a !important;
        box-shadow: 0 0 10px rgba(76, 195, 138, 0.3) !important;
    }}

    div.st-key-titan_chat_window form button {{
        background: linear-gradient(135deg, #4cc38a, #3aa8c8) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        height: 38px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(76, 195, 138, 0.35) !important;
        padding: 0 !important;
    }}

    /* Mobile Responsive (< 600px) */
    @media (max-width: 600px) {{
        div.st-key-titan_chat_window {{
            width: calc(100vw - 32px) !important;
            right: 16px !important;
            left: 16px !important;
            bottom: 92px !important;
        }}
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: var(--bg-alt) !important;
        border-right: 1px solid var(--border) !important;
    }}

    .sb-brand-box {{
        padding: 1.5rem 1.25rem 1.25rem;
        background: linear-gradient(180deg, {th['primary_dim']} 0%, transparent 100%);
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.25rem;
    }}

    .sb-title-row {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.75rem;
    }}

    .sb-icon-orb {{
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: {th['logo_gradient']};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 16px {th['primary_glow']};
    }}

    .sb-brand-name {{
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }}

    .sb-brand-tag {{
        font-size: 0.72rem;
        color: var(--primary-light);
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 100px;
        background: var(--primary-dim);
        border: 1px solid var(--border);
        color: var(--primary-light);
    }}

    .status-pill.offline {{
        background: rgba(244, 63, 94, 0.15);
        border-color: rgba(244, 63, 94, 0.35);
        color: #F43F5E;
    }}

    .live-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: currentColor;
        box-shadow: 0 0 8px currentColor;
        animation: pulse 1.8s infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}

    /* Top Telemetry KPI Bar */
    .telemetry-bar {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 1.5rem;
    }}

    .kpi-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1.25rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}

    .kpi-card:hover {{
        border-color: var(--border-hover);
        transform: translateY(-2px);
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        opacity: 0.8;
    }}

    .kpi-label {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.4rem;
    }}

    .kpi-value {{
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .kpi-sub {{
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }}

    /* Section Cards */
    .ops-panel {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        position: relative;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}

    .panel-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.25rem;
    }}

    .panel-title {{
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .panel-subtitle {{
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 2px;
    }}

    /* Agent Mesh Grid */
    .agent-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 1rem;
    }}

    .agent-card {{
        background: var(--bg-alt);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem;
        position: relative;
        transition: all 0.2s ease;
    }}

    .agent-card:hover {{
        border-color: var(--border-hover);
        transform: translateY(-2px);
    }}

    .agent-head {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }}

    .agent-role {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .agent-model-pill {{
        font-size: 0.68rem;
        font-family: 'JetBrains Mono', monospace;
        padding: 3px 8px;
        border-radius: 6px;
        background: var(--primary-dim);
        border: 1px solid var(--border);
        color: var(--primary-light);
    }}

    .agent-desc {{
        font-size: 0.78rem;
        color: var(--text-2);
        line-height: 1.45;
        margin-bottom: 0.75rem;
    }}

    .agent-tools {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }}

    .tool-badge {{
        font-size: 0.67rem;
        font-family: 'JetBrains Mono', monospace;
        padding: 2px 7px;
        border-radius: 4px;
        background: var(--glass);
        border: 1px solid var(--border);
        color: var(--primary-light);
    }}

    /* Real-Time Live Log Window */
    .terminal-box {{
        background: #04070D;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.77rem;
        max-height: 380px;
        overflow-y: auto;
    }}

    .terminal-line {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }}

    .terminal-line:hover {{
        background: rgba(255, 255, 255, 0.03);
    }}

    .t-agent {{
        font-size: 0.66rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 4px;
        background: var(--glass);
        border: 1px solid var(--border);
        color: var(--primary-light);
        min-width: 80px;
        text-align: center;
    }}

    .t-msg {{
        flex: 1;
        color: var(--text-2);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}

    .t-file {{
        font-size: 0.7rem;
        color: var(--accent);
    }}

    /* Buttons */
    .stButton > button {{
        background: {th['gradient']} !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.5rem !important;
        box-shadow: 0 4px 18px {th['primary_glow']} !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px {th['primary_glow']} !important;
    }}

    /* Custom Scrollbars */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--surface-3); border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--primary-light); }}
</style>
""",
    unsafe_allow_html=True,
)

# ── API Configurations ─────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000"

# ── Session State Initializer ──────────────────────────────────────────────
defaults = {
    "user_request": "",
    "build_id": None,
    "build_done": False,
    "build_result": None,
    "events_seen": 0,
    "copilot_messages": [
        {
            "role": "assistant",
            "content": "👋 **Hello! I'm TITAN AI Copilot.**\n\nI can help you architect complete software projects, design schemas, suggest tech stacks, and generate prompts for TITAN's autonomous build engine.\n\n*What would you like to build today?*",
        }
    ],
    "active_tab": "Command Center",
    "selected_explorer_project": "",
    "selected_explorer_file": "",
    "benchmark_data": None,
    "playground_result": None,
    "chatbot_open": False,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── Backend Client Helpers ─────────────────────────────────────────────────
def check_backend_health() -> tuple[bool, dict]:
    try:
        res = requests.get(f"{API_URL}/health", timeout=3)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, {}


def trigger_build(request_text: str, auto_push: bool, auto_open: bool, private: bool, branches: list[str]) -> str:
    res = requests.post(
        f"{API_URL}/build",
        json={
            "request": request_text,
            "auto_push": auto_push,
            "auto_open_vscode": auto_open,
            "private_repo": private,
            "extra_branches": branches,
        },
        timeout=10,
    )
    return res.json().get("build_id", "")


def poll_build_status(build_id: str) -> dict:
    res = requests.get(f"{API_URL}/build/{build_id}", timeout=5)
    return res.json()


def poll_build_events(build_id: str, since: int = 0) -> dict:
    res = requests.get(f"{API_URL}/build/{build_id}/events", params={"since": since}, timeout=5)
    return res.json()


def fetch_projects() -> list[dict]:
    try:
        res = requests.get(f"{API_URL}/projects", timeout=5)
        raw_list = res.json().get("projects", [])
        seen: set[str] = set()
        unique = []
        for p in raw_list:
            if p.get("name") and p["name"] not in seen:
                seen.add(p["name"])
                unique.append(p)
        return unique
    except Exception:
        return []


def query_copilot(message: str, history: list[dict]) -> str:
    """Send question to backend Copilot endpoint or perform intelligent offline response."""
    try:
        res = requests.post(
            f"{API_URL}/chat",
            json={"message": message, "history": history[-4:]},
            timeout=25,
        )
        if res.status_code == 200:
            return res.json().get("reply", "")
    except Exception:
        pass

    # High quality local fallback response if backend is offline
    return (
        f"⚡ **TITAN AI Copilot**\n\n"
        f"Here is a recommended production blueprint for: **'{message}'**\n\n"
        f"### 🏗️ Architecture & Tech Stack\n"
        f"- **Backend Service:** FastAPI with async routes, Pydantic v2 schemas, and dependency injection.\n"
        f"- **Persistence:** SQLite / PostgreSQL with SQLAlchemy 2.0 async engine.\n"
        f"- **Authentication & Security:** JWT Bearer tokens with bcrypt password hashing.\n"
        f"- **Frontend / Consumer:** Responsive Dark Console or RESTful Swagger / ReDoc endpoints.\n"
        f"- **Testing & CI/CD:** Pytest test suite with GitHub Actions workflow automation.\n\n"
        f"💡 **TITAN Build Prompt:**\n"
        f"`Build a {message} featuring modular code architecture, database persistence, unit tests, and comprehensive OpenAPI documentation.`\n\n"
        f"*Click 'Use as Project Prompt' below to load this blueprint into the launcher!*"
    )


def fetch_project_files(project_name: str) -> list[str]:
    """Fetch list of all generated files in a project."""
    try:
        res = requests.get(f"{API_URL}/projects/{project_name}/files", timeout=5)
        if res.status_code == 200:
            return res.json().get("files", [])
    except Exception:
        pass
    return []


def fetch_file_content(project_name: str, file_path: str) -> str:
    """Fetch the text content of a project file."""
    try:
        res = requests.get(
            f"{API_URL}/projects/{project_name}/file",
            params={"file_path": file_path},
            timeout=5,
        )
        if res.status_code == 200:
            return res.json().get("content", "")
    except Exception as e:
        return f"Error loading file: {e}"
    return "File unavailable or empty."


def open_in_vscode(project_name: str) -> bool:
    """Trigger backend to open the project directory in VS Code."""
    try:
        res = requests.post(f"{API_URL}/projects/{project_name}/open_vscode", timeout=5)
        return res.status_code == 200 and res.json().get("success", False)
    except Exception:
        return False


def enhance_prompt_api(prompt: str, target_stack: str = "auto") -> str:
    """Call backend AI architect to expand a brief prompt into a production specification."""
    try:
        res = requests.post(
            f"{API_URL}/prompt/enhance",
            json={"prompt": prompt, "target_stack": target_stack},
            timeout=20,
        )
        if res.status_code == 200:
            return res.json().get("enhanced", prompt)
    except Exception:
        pass
    return f"Build a production-ready {prompt} featuring modular architecture, relational database persistence, Pydantic schemas, unit tests, and comprehensive documentation."


def ping_providers_api() -> dict:
    """Ping all backend AI providers to measure live latency and availability."""
    try:
        res = requests.get(f"{API_URL}/system/ping_providers", timeout=10)
        if res.status_code == 200:
            return res.json().get("providers", {})
    except Exception:
        pass
    return {}


# ── Health Check ───────────────────────────────────────────────────────────
is_online, health_data = check_backend_health()
providers = health_data.get("providers", ["gemini", "groq", "mistral"])
projects_list = fetch_projects()
total_projects = len(projects_list)

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION & TELEMETRY
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        f"""
<div class="sb-brand-box">
    <div class="sb-title-row">
        <div class="sb-icon-orb">⚡</div>
        <div>
            <div class="sb-brand-name">Project TITAN</div>
            <div class="sb-brand-tag">Autonomous AI Engine</div>
        </div>
    </div>
    <div class="status-pill {'offline' if not is_online else ''}">
        <span class="live-dot"></span>
        {'System Online · All Agents Ready' if is_online else 'Backend Offline (Port 8000)'}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 🎨 Color Palette")
    chosen_palette = st.selectbox(
        "Theme Palette",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.get("theme_palette", "Cyber Emerald (Ops Console)")),
        label_visibility="collapsed",
    )
    if chosen_palette != st.session_state.get("theme_palette"):
        st.session_state["theme_palette"] = chosen_palette
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    nav_options = ["Command Center", "Project Explorer", "Agent Mesh & Playground", "Engine Diagnostics"]
    current_active = st.session_state.get("active_tab", "Command Center")
    if current_active not in nav_options:
        current_active = "Command Center"
    current_nav_index = nav_options.index(current_active)
    nav_selection = st.radio(
        "Navigation",
        options=nav_options,
        index=current_nav_index,
        label_visibility="collapsed",
    )
    if nav_selection != st.session_state.get("active_tab"):
        st.session_state["active_tab"] = nav_selection
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Build Options")
    auto_push = st.toggle("Push to GitHub", value=True)
    auto_open = st.toggle("Open in VS Code", value=True)
    private_repo = st.toggle("Private repository", value=False)
    branches_str = st.text_input("Git branches", value="develop, main")
    extra_branches = [b.strip() for b in branches_str.split(",") if b.strip()]

    st.markdown("---")
    st.markdown("### 📜 Recent Projects")
    if projects_list:
        # Deduplicate by project name before rendering to avoid duplicate widget keys
        seen_names: set[str] = set()
        unique_projects = []
        for p in projects_list:
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                unique_projects.append(p)
        for idx, p in enumerate(unique_projects[:6]):
            p_name = p['name']
            col_rp1, col_rp2 = st.columns([4, 1])
            with col_rp1:
                if st.button(f"⚡ {p_name}", key=f"sb_proj_{idx}_{p_name}", width="stretch"):
                    st.session_state["selected_explorer_project"] = p_name
                    st.session_state["active_tab"] = "Project Explorer"
                    st.rerun()
            with col_rp2:
                st.caption(f"{p.get('completed_tasks', 0)}/{p.get('total_tasks', 0)}")
    else:
        st.caption("No builds recorded yet")


# ══════════════════════════════════════════════════════════════════════════
# FLOATING CHATBOT WIDGET (BOTTOM-RIGHT CORNER)
# ══════════════════════════════════════════════════════════════════════════
is_chat_open = st.session_state.get("chatbot_open", False)

# 1. Expanded Chat Window (anchored above launcher: bottom: 96px, right: 24px)
if is_chat_open:
    with st.container(key="titan_chat_window"):
        # Header: Big logo + "Support System" + "Online" status + close (✕) button
        col_h_left, col_h_right = st.columns([5, 1])
        with col_h_left:
            st.markdown(
                """
<div style="display:flex;align-items:center;gap:12px;padding:12px 14px 8px;">
    <div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg, #4cc38a, #3aa8c8);display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 14px rgba(76,195,138,0.45);color:#FFF;border:1px solid rgba(255,255,255,0.3);flex-shrink:0;">
        ⚡
    </div>
    <div>
        <div style="font-weight:800;font-size:1.05rem;color:#FFFFFF;line-height:1.2;letter-spacing:-0.01em;">Support System</div>
        <div style="font-size:0.72rem;color:#34D399;display:flex;align-items:center;gap:4px;margin-top:2px;">
            <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;"></span>
            Online · 24/7 AI Desk
        </div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
        with col_h_right:
            st.markdown("<div style='padding-top:8px;'></div>", unsafe_allow_html=True)
            if st.button("✕", key="titan_chat_close_btn", help="Close Support"):
                st.session_state["chatbot_open"] = False
                st.rerun()

        st.markdown("<div style='border-bottom:1px solid rgba(76,195,138,0.18);margin:0 0 8px 0;'></div>", unsafe_allow_html=True)

        # Body: Scrollable message container
        chat_body = st.container(height=360)
        with chat_body:
            if not st.session_state["copilot_messages"]:
                st.markdown(
                    """
<div style="padding:14px;background:rgba(76,195,138,0.06);border:1px dashed rgba(76,195,138,0.25);border-radius:12px;margin:8px 0 12px;">
    <div style="font-size:0.86rem;font-weight:700;color:#FFFFFF;margin-bottom:4px;">👋 Hello! I'm your Support System</div>
    <div style="font-size:0.76rem;color:var(--text-muted);line-height:1.4;">
        I can help you design system architectures, craft build specifications, debug errors, or generate ready-to-run prompts.
    </div>
</div>
""",
                    unsafe_allow_html=True,
                )
                st.caption("Quick Blueprints:")
                q1, q2 = st.columns(2)
                with q1:
                    if st.button("💡 SaaS API", key="chat_quick_1", width="stretch"):
                        _p = "Build a FastAPI subscription billing REST API with Stripe webhooks, SQLite, and JWT auth"
                        st.session_state["copilot_messages"].append({"role": "user", "content": _p})
                        _reply = query_copilot(_p, st.session_state["copilot_messages"])
                        st.session_state["copilot_messages"].append({"role": "assistant", "content": _reply})
                        st.rerun()
                with q2:
                    if st.button("🤖 Telegram Bot", key="chat_quick_2", width="stretch"):
                        _p = "Build an autonomous Telegram AI assistant bot in Python with LangChain and SQLite memory"
                        st.session_state["copilot_messages"].append({"role": "user", "content": _p})
                        _reply = query_copilot(_p, st.session_state["copilot_messages"])
                        st.session_state["copilot_messages"].append({"role": "assistant", "content": _reply})
                        st.rerun()

            for idx, msg in enumerate(st.session_state["copilot_messages"]):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "💡 **TITAN Build Prompt:**" in msg["content"]:
                        try:
                            extracted = msg["content"].split("`Build a ")[1].split("`")[0]
                            clean_prompt = f"Build a {extracted}"
                            if st.button("✨ Use as Project Prompt", key=f"use_prompt_widget_{idx}", width="stretch"):
                                st.session_state["user_request"] = clean_prompt
                                st.session_state["active_tab"] = "Command Center"
                                st.session_state["chatbot_open"] = False
                                st.rerun()
                        except Exception:
                            pass

        # Footer: Text Input + Send Button inside an st.form (contained inside chat window!)
        with st.form("titan_chat_form", clear_on_submit=True):
            fc1, fc2 = st.columns([5, 1])
            with fc1:
                user_msg = st.text_input(
                    "Message",
                    placeholder="Ask TITAN Assistant...",
                    label_visibility="collapsed",
                    key="titan_chat_input_val",
                )
            with fc2:
                submitted = st.form_submit_button("➤", width="stretch")

        if submitted and user_msg and user_msg.strip():
            cleaned_input = user_msg.strip()
            st.session_state["copilot_messages"].append({"role": "user", "content": cleaned_input})
            bot_reply = query_copilot(cleaned_input, st.session_state["copilot_messages"])
            st.session_state["copilot_messages"].append({"role": "assistant", "content": bot_reply})
            st.rerun()

# 2. Circular Launcher Button (fixed at bottom-right corner: bottom: 24px, right: 24px)
launcher_icon = "✕" if is_chat_open else "⚡"
launcher_help = "Close Support" if is_chat_open else "Support System · 24/7 AI Desk"
if st.button(launcher_icon, key="titan_chat_launcher", help=launcher_help):
    st.session_state["chatbot_open"] = not is_chat_open
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# MAIN VIEW ROUTER
# ══════════════════════════════════════════════════════════════════════════
current_tab = st.session_state.get("active_tab", "Command Center")

# ---------------------------------------------------------------------------
# TAB 1: COMMAND CENTER
# ---------------------------------------------------------------------------
if current_tab == "Command Center":
    # Main Project Prompt Input
    user_request_val = st.text_area(
        "Project Blueprint Specification",
        value=st.session_state.get("user_request", ""),
        placeholder="e.g. Build a production-ready FastAPI Todo REST API with SQLite database, JWT authentication, Pydantic schemas, and Pytest unit tests...",
        height=140,
        help="Specify the software system you want TITAN to plan, write, test, and ship.",
    )
    st.session_state["user_request"] = user_request_val

    btn_col1, btn_col2, btn_col3 = st.columns([3, 2, 1])
    with btn_col1:
        launch_clicked = st.button("⚡  Launch Autonomous Build", disabled=not user_request_val.strip(), width="stretch")
    with btn_col2:
        enhance_clicked = st.button("✨ AI Prompt Architect", disabled=not user_request_val.strip(), width="stretch", help="Let TITAN's Principal Architect expand your idea into a production specification")
    with btn_col3:
        if st.button("🗑️ Clear", width="stretch"):
            st.session_state["user_request"] = ""
            st.rerun()

    if enhance_clicked and user_request_val.strip():
        with st.spinner("AI Architect is designing optimal schemas and system specifications..."):
            enhanced = enhance_prompt_api(user_request_val, target_stack="auto")
            st.session_state["user_request"] = enhanced
            st.toast("Blueprint architected with production specifications!", icon="✨")
            st.rerun()

    if not is_online:
        st.warning("⚠️ Backend API server is offline. Run `python -m backend.main` in your terminal to start it.")

    if launch_clicked and user_request_val.strip():
        if not is_online:
            st.error("Cannot launch build: Backend is offline.")
        else:
            st.session_state.update({"build_id": None, "build_done": False, "build_result": None, "events_seen": 0})
            try:
                b_id = trigger_build(
                    request_text=user_request_val,
                    auto_push=auto_push,
                    auto_open=auto_open,
                    private=private_repo,
                    branches=extra_branches,
                )
                st.session_state["build_id"] = b_id
                st.rerun()
            except Exception as e:
                st.error(f"Failed to launch build: {e}")

    # Live Build Monitor
    if st.session_state.get("build_id") and not st.session_state.get("build_done"):
        build_id = st.session_state["build_id"]
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        progress_slot = st.empty()
        log_slot = st.empty()
        events_seen = st.session_state.get("events_seen", 0)
        all_events: list = []

        while True:
            try:
                status_data = poll_build_status(build_id)
                events_data = poll_build_events(build_id, since=events_seen)
                new_events = events_data.get("events", [])
                all_events.extend(new_events)
                events_seen += len(new_events)
                st.session_state["events_seen"] = events_seen

                pct = int(status_data.get("progress", 0))
                current_action = status_data.get("current_action", "Engineering system...")
                current_agent = status_data.get("current_agent", "planner")

                with progress_slot.container():
                    st.markdown(
                        f"""
<div class="ops-panel" style="border-color:var(--primary)">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem">
        <div style="display:flex;align-items:center;gap:10px">
            <span class="live-dot" style="color:var(--primary)"></span>
            <span style="font-weight:800;font-size:1rem;color:#FFF">Autonomous Build in Progress...</span>
        </div>
        <span style="font-family:'JetBrains Mono',monospace;font-weight:800;color:var(--primary-light);font-size:1.1rem">{pct}%</span>
    </div>
""",
                        unsafe_allow_html=True,
                    )
                    st.progress(pct / 100)
                    st.markdown(
                        f"""
    <div style="margin-top:0.9rem;font-size:0.85rem;color:var(--text-2);display:flex;align-items:center;gap:8px">
        <span class="tool-badge" style="color:var(--primary-light);border-color:var(--border)">AGENT: {current_agent.upper()}</span>
        <span>{current_action}</span>
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                # Format terminal log lines
                log_rows = ""
                for ev in reversed(all_events[-50:]):
                    ag = ev.get("agent", "titan")
                    act = ev.get("action", "")
                    msg = ev.get("message", "")
                    fp = ev.get("file_path", "")
                    file_span = f'<span class="t-file">→ {fp}</span>' if fp else ""
                    log_rows += f"""
<div class="terminal-line">
    <span class="t-agent">{ag}</span>
    <span class="t-msg"><b>{act}</b> {msg}</span>
    {file_span}
</div>
"""
                _empty = '<div style="color:var(--text-faint);padding:8px">Awaiting telemetry stream from orchestrator...</div>'
                log_slot.markdown(f'<div class="terminal-box">{log_rows or _empty}</div>', unsafe_allow_html=True)

                if status_data.get("status") in ("done", "failed"):
                    st.session_state["build_done"] = True
                    st.session_state["build_result"] = status_data.get("result", {})
                    break

            except Exception as e:
                st.session_state.update({"build_done": True, "build_result": {"success": False, "error": str(e)}})
                break

            time.sleep(2)
        st.rerun()

    # Result Display
    if st.session_state.get("build_done") and st.session_state.get("build_result"):
        res = st.session_state["build_result"]
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        if res.get("success"):
            files = res.get("files_created", [])
            duration = res.get("duration_seconds", 0)
            tasks = res.get("tasks_completed", 0)
            gh_url = res.get("github_url", "")

            p_name = res.get("project_name", "Project")
            st.markdown(
                f"""
<div class="ops-panel" style="border-color:var(--primary);box-shadow:0 0 40px {th['primary_glow']}">
    <div style="font-size:1.35rem;font-weight:900;color:#FFF;margin-bottom:0.4rem">
        🎉 Build Finished Successfully: {p_name}
    </div>
    <div style="font-size:0.8rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;margin-bottom:1.25rem">
        Duration: {duration:.1f}s &nbsp;·&nbsp; Total Tasks Executed: {tasks} &nbsp;·&nbsp; Files Generated: {len(files)}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            act_c1, act_c2, act_c3 = st.columns(3)
            with act_c1:
                if st.button("💻 Open in VS Code", key="post_open_vscode", width="stretch"):
                    if open_in_vscode(p_name):
                        st.toast(f"Opened {p_name} in VS Code!", icon="💻")
                    else:
                        st.warning("Could not launch VS Code CLI.")
            with act_c2:
                if st.button("📂 Inspect in Project Explorer", key="post_inspect_proj", width="stretch"):
                    st.session_state["selected_explorer_project"] = p_name
                    st.session_state["active_tab"] = "Project Explorer"
                    st.rerun()
            with act_c3:
                if gh_url:
                    st.link_button("⬡ View on GitHub ↗", gh_url, width="stretch")
                else:
                    st.button("Local Repository Only", disabled=True, width="stretch")

            if files:
                st.markdown("##### 📁 Artifacts & Files Generated")
                cols = st.columns(2)
                for i, file_path in enumerate(files):
                    with cols[i % 2]:
                        st.markdown(
                            f'<div class="terminal-line" style="border:1px solid var(--border);border-radius:6px;margin-bottom:6px"><span style="color:var(--primary-light)">◈</span> <span style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem">{file_path}</span></div>',
                            unsafe_allow_html=True,
                        )

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            if st.button("⚡ Build Another Project", width="stretch"):
                st.session_state["build_id"] = None
                st.session_state["build_done"] = False
                st.session_state["build_result"] = None
                st.rerun()

        else:
            st.markdown(
                f"""
<div class="ops-panel" style="border-color:var(--rose)">
    <div style="font-size:1.25rem;font-weight:900;color:var(--rose)">❌ Build Encountered Errors</div>
    <div style="font-size:0.85rem;color:var(--text-2);margin-top:0.5rem">{res.get('error', 'Diagnostics captured in logs above.')}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            if st.button("↩ Try Again", width="stretch"):
                st.session_state["build_id"] = None
                st.session_state["build_done"] = False
                st.rerun()


# ---------------------------------------------------------------------------
# TAB 2: PROJECT EXPLORER & CODE VIEWER
# ---------------------------------------------------------------------------
elif current_tab == "Project Explorer":
    st.markdown(
        """
<div class="ops-panel">
    <div class="panel-header">
        <div>
            <div class="panel-title">📁 Autonomous Project Explorer & Code Studio</div>
            <div class="panel-subtitle">Inspect source code, dependency configurations, and documentation for all autonomously built software systems.</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if not projects_list:
        st.info("No projects created yet. Launch your first build from the Command Center!")
    else:
        proj_names = [p["name"] for p in projects_list]
        default_proj = st.session_state.get("selected_explorer_project")
        if default_proj not in proj_names:
            default_proj = proj_names[0]
            st.session_state["selected_explorer_project"] = default_proj

        selected_proj = st.selectbox(
            "Select Project to Inspect",
            options=proj_names,
            index=proj_names.index(default_proj),
            label_visibility="collapsed",
        )
        st.session_state["selected_explorer_project"] = selected_proj

        # Find project info
        p_info = next((p for p in projects_list if p["name"] == selected_proj), {})

        # Top Project Header & Quick Actions
        col_meta1, col_meta2 = st.columns([3, 2])
        with col_meta1:
            st.markdown(f"### ⚡ `{selected_proj}`")
            st.caption(p_info.get("description", "No description provided"))
            st.markdown(
                f"""
<div style="display:flex;gap:12px;font-size:0.75rem;margin-top:4px;color:var(--text-muted);font-family:'JetBrains Mono',monospace">
    <span>Tasks: <b>{p_info.get('completed_tasks', 0)}/{p_info.get('total_tasks', 0)}</b></span>
    <span>Status: <b style="color:var(--primary)">{p_info.get('status', 'done').upper()}</b></span>
    <span>Created: {p_info.get('created_at', '')[:10]}</span>
</div>
""",
                unsafe_allow_html=True,
            )

        with col_meta2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                if st.button("💻 VS Code", key="exp_open_vscode", width="stretch"):
                    if open_in_vscode(selected_proj):
                        st.toast(f"Opened {selected_proj} in VS Code!", icon="💻")
                    else:
                        st.warning("Could not launch VS Code CLI.")
            with act_col2:
                gh_url = p_info.get("github_url", "")
                if gh_url:
                    st.link_button("🌿 GitHub ↗", gh_url, width="stretch")
                else:
                    st.button("Local Only", disabled=True, width="stretch")
            with act_col3:
                # Prepare in-memory ZIP
                proj_dir = Path(health_data.get("projects_dir", "projects")) / selected_proj
                zip_bytes = io.BytesIO()
                if proj_dir.exists():
                    with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
                        for f in proj_dir.rglob("*"):
                            if f.is_file() and not any(part in (".git", "__pycache__", "node_modules") for part in f.parts):
                                zf.write(f, arcname=str(f.relative_to(proj_dir)))
                    st.download_button(
                        "📥 ZIP Archive",
                        data=zip_bytes.getvalue(),
                        file_name=f"{selected_proj}.zip",
                        mime="application/zip",
                        width="stretch",
                    )
                else:
                    st.button("Archive N/A", disabled=True, width="stretch")

        st.markdown("---")

        # Fetch files
        files = fetch_project_files(selected_proj)
        if not files:
            st.warning("No files found in this project workspace directory.")
        else:
            col_tree, col_code = st.columns([1, 2])

            with col_tree:
                st.markdown("##### 📄 Project Files")
                current_file = st.session_state.get("selected_explorer_file")
                if current_file not in files:
                    current_file = "README.md" if "README.md" in files else files[0]
                    st.session_state["selected_explorer_file"] = current_file

                selected_file = st.radio(
                    "Files",
                    options=files,
                    index=files.index(current_file),
                    label_visibility="collapsed",
                )
                st.session_state["selected_explorer_file"] = selected_file

            with col_code:
                content = fetch_file_content(selected_proj, selected_file)
                ext = Path(selected_file).suffix.lower().lstrip(".")
                lang_map = {
                    "py": "python",
                    "json": "json",
                    "md": "markdown",
                    "yml": "yaml",
                    "yaml": "yaml",
                    "sh": "bash",
                    "js": "javascript",
                    "ts": "typescript",
                    "html": "html",
                    "css": "css",
                    "txt": "text",
                    "gitignore": "text",
                }
                lang = lang_map.get(ext, "text")

                # Code Header
                st.markdown(
                    f"""
<div style="display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--border);padding:8px 14px;border-radius:8px;margin-bottom:8px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#FFF;font-weight:700">
        📄 {selected_file}
    </div>
    <div style="display:flex;gap:8px;align-items:center">
        <span class="tool-badge">{lang.upper()}</span>
        <span style="font-size:0.75rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace">{len(content)} chars</span>
    </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                if ext == "md":
                    tab_preview, tab_raw = st.tabs(["🎨 Formatted Preview", "📝 Raw Source"])
                    with tab_preview:
                        st.markdown(content)
                    with tab_raw:
                        st.code(content, language="markdown", line_numbers=True)
                else:
                    st.code(content, language=lang, line_numbers=True)

                st.download_button(
                    label=f"💾 Download {Path(selected_file).name}",
                    data=content,
                    file_name=Path(selected_file).name,
                    mime="text/plain",
                )


# ---------------------------------------------------------------------------
# TAB 3: AGENT MESH & PLAYGROUND
# ---------------------------------------------------------------------------
elif current_tab == "Agent Mesh & Playground":
    st.markdown(
        """
<div class="ops-panel">
    <div class="panel-header">
        <div>
            <div class="panel-title">📡 Autonomous Agent Mesh & Interactive Lab</div>
            <div class="panel-subtitle">TITAN operates 6 specialized CAMEL AI agents coordinating through structured memory, toolkits, and closed-loop feedback.</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Architecture Coordination Flowchart
    st.markdown(
        """
<div class="ops-panel" style="padding:1.25rem;background:var(--bg-alt);border:1px dashed var(--border)">
    <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.75rem">
        🔄 Autonomous Agent Coordination Loop
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;font-family:'JetBrains Mono',monospace;font-size:0.78rem">
        <span class="status-pill">1. User Blueprint</span>
        <span style="color:var(--text-faint)">➔</span>
        <span class="tool-badge" style="background:var(--primary-dim);color:var(--primary-light)">🧠 Planner Agent</span>
        <span style="color:var(--text-faint)">➔</span>
        <span class="tool-badge" style="background:var(--primary-dim);color:var(--primary-light)">⚙️ Code Engineer</span>
        <span style="color:var(--text-faint)">⇄</span>
        <span class="tool-badge" style="background:var(--primary-dim);color:var(--primary-light)">🧪 QA Diagnostic</span>
        <span style="color:var(--text-faint)">➔</span>
        <span class="tool-badge" style="background:var(--primary-dim);color:var(--primary-light)">📝 Docs Agent</span>
        <span style="color:var(--text-faint)">➔</span>
        <span class="tool-badge" style="background:var(--primary-dim);color:var(--primary-light)">🚀 GitHub VCS</span>
        <span style="color:var(--text-faint)">➔</span>
        <span class="status-pill">Deployed Workspace</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("##### 🤖 Active Agent Specifications")
    agent_specs = [
        ("🧠 Planner Agent", "Gemini 2.5 Flash", "Deconstructs prompt into validated DAG task tree", ["validate_plan", "schema_enforcement", "dependency_ordering"]),
        ("⚙️ Code Engineer", "Gemini 2.5 Flash / Groq", "Synthesizes production code with zero placeholders", ["write_code", "syntax_linting", "ast_validation"]),
        ("🧪 QA & Diagnostic Tester", "Gemini 2.5 Flash", "Executes terminal commands & diagnoses root causes", ["run_command", "read_manifests", "log_analysis"]),
        ("📝 Documentation Agent", "Gemini / Groq / Mistral", "Generates comprehensive README, architectural diagrams", ["list_directory", "read_file", "write_file"]),
        ("💻 Terminal Sandbox", "Subprocess macOS / Linux", "Runs build tools, dependency installers, test runners", ["python_alias", "pip_sandbox", "safe_cwd"]),
        ("🚀 GitHub & VCS Toolkit", "PyGithub + Git CLI", "Creates remote repos, commits atomic stages, pushes branches", ["create_repo", "push_branches", "set_remotes"]),
    ]

    st.markdown('<div class="agent-grid">', unsafe_allow_html=True)
    for title, model, role, tools in agent_specs:
        tools_html = "".join([f'<span class="tool-badge">{t}</span>' for t in tools])
        st.markdown(
            f"""
<div class="agent-card">
    <div class="agent-head">
        <div class="agent-role">{title}</div>
        <span class="agent-model-pill">{model}</span>
    </div>
    <div class="agent-desc">{role}</div>
    <div class="agent-tools">{tools_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Interactive Agent Testing Playground
    st.markdown("##### 🧪 Interactive Agent Testing Playground")
    st.caption("Directly test individual agents inside the TITAN mesh with custom prompts and inspect real-time outputs.")

    pg_col1, pg_col2 = st.columns([1, 2])
    sample_prompts = {
        "Planner Agent (DAG Decomposition)": "Plan a Redis cache microservice with TTL eviction and token bucket rate limiter in Python",
        "Code Engineer (Syntax & Implementation)": "Write a FastAPI router file with JWT auth bearer and healthcheck endpoint",
        "Docs Agent (README & Architecture)": "Generate a comprehensive README.md with ASCII diagram for an async webhook dispatcher",
    }
    with pg_col1:
        test_agent_choice = st.selectbox(
            "Select Agent to Test",
            ["Planner Agent (DAG Decomposition)", "Code Engineer (Syntax & Implementation)", "Docs Agent (README & Architecture)"],
        )
        if st.button("📋 Load Sample Prompt", width="stretch"):
            st.session_state["playground_prompt"] = sample_prompts[test_agent_choice]
            st.rerun()

    with pg_col2:
        pg_input = st.text_area(
            "Test Instruction / Context",
            value=st.session_state.get("playground_prompt", sample_prompts["Planner Agent (DAG Decomposition)"]),
            height=95,
        )
        st.session_state["playground_prompt"] = pg_input
        if st.button("⚡ Run Live Agent Experiment", width="stretch"):
            with st.spinner(f"Executing {test_agent_choice}..."):
                t_start = time.time()
                try:
                    from camel.agents import ChatAgent
                    from backend.ai.model_factory import get_gemini_model, get_groq_model

                    if "Planner" in test_agent_choice:
                        model = get_gemini_model("gemini-2.5-flash")
                        agent = ChatAgent(system_message="You are TITAN's Planner Agent. Output a clean task breakdown in structured JSON or markdown.", model=model)
                    elif "Code" in test_agent_choice:
                        model = get_groq_model("openai/gpt-oss-120b")
                        agent = ChatAgent(system_message="You are TITAN's Code Engineer. Output raw production code without markdown fences.", model=model)
                    else:
                        model = get_gemini_model("gemini-2.5-flash")
                        agent = ChatAgent(system_message="You are TITAN's Documentation Agent. Output a comprehensive README with features and architecture.", model=model)

                    resp = agent.step(pg_input)
                    latency = round((time.time() - t_start) * 1000, 1)
                    output_text = resp.msgs[0].content if resp.msgs else "No response generated."
                    st.session_state["playground_result"] = {
                        "agent": test_agent_choice,
                        "output": output_text,
                        "latency_ms": latency,
                    }
                except Exception as e:
                    st.session_state["playground_result"] = {
                        "agent": test_agent_choice,
                        "output": f"Experiment error: {e}",
                        "latency_ms": round((time.time() - t_start) * 1000, 1),
                    }
                st.rerun()

    if st.session_state.get("playground_result"):
        res = st.session_state["playground_result"]
        st.markdown(
            f"""
<div class="ops-panel" style="margin-top:1rem;border-color:var(--primary)">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem">
        <b>Output from {res['agent']}</b>
        <span class="agent-model-pill">⏱️ {res['latency_ms']} ms</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.code(res["output"], language="markdown" if "Docs" in res["agent"] else "python")


# ---------------------------------------------------------------------------
# TAB 4: ENGINE DIAGNOSTICS & TELEMETRY
# ---------------------------------------------------------------------------
elif current_tab == "Engine Diagnostics":
    st.markdown(
        """
<div class="ops-panel">
    <div class="panel-header">
        <div>
            <div class="panel-title">⚙️ API Engine & System Diagnostics</div>
            <div class="panel-subtitle">Real-time status of AI model providers, credentials, latency benchmarks, and local workspaces.</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Live Latency Benchmark Bar
    st.markdown("##### ⚡ Live Provider Latency Benchmark")
    col_bench_btn, _ = st.columns([2, 5])
    with col_bench_btn:
        if st.button("🚀 Run Live Latency Benchmark", width="stretch"):
            with st.spinner("Benchmarking Groq, Gemini, and Mistral endpoints..."):
                st.session_state["benchmark_data"] = ping_providers_api()
                st.toast("Benchmark completed!", icon="⚡")
                st.rerun()

    bench_data = st.session_state.get("benchmark_data") or ping_providers_api()
    if bench_data:
        b_cols = st.columns(len(bench_data))
        for col, (prov, data) in zip(b_cols, bench_data.items()):
            with col:
                st.markdown(
                    f"""
<div class="kpi-card" style="border-left:3px solid var(--primary)">
    <div class="kpi-label">{prov.upper()} API</div>
    <div class="kpi-value">{data.get('latency_ms', 0)} ms</div>
    <div class="kpi-sub">{data.get('model', 'Active')} · <span style="color:var(--primary-light)">ONLINE</span></div>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        st.markdown("##### 🔑 API Providers Status")
        prov_list = health_data.get("providers", [])
        for prov in ["gemini", "groq", "mistral"]:
            has_p = prov in prov_list
            color = "#10B981" if has_p else "#EF4444"
            st.markdown(
                f"""
<div class="terminal-line" style="border:1px solid var(--border);border-radius:8px;margin-bottom:8px">
    <span style="color:{color}">●</span>
    <b style="text-transform:uppercase">{prov} API</b>
    <span style="margin-left:auto;font-size:0.75rem;color:var(--text-muted)">{'Configured & Active' if has_p else 'Missing Key'}</span>
</div>
""",
                unsafe_allow_html=True,
            )

    with col_diag2:
        st.markdown("##### 📁 System Workspaces & Storage")
        p_dir = health_data.get("projects_dir", "projects/")
        proj_dir_path = Path(p_dir)
        total_size_mb = 0.0
        if proj_dir_path.exists():
            total_size_mb = round(sum(f.stat().st_size for f in proj_dir_path.rglob('*') if f.is_file()) / (1024 * 1024), 2)

        st.markdown(
            f"""
<div class="terminal-line" style="border:1px solid var(--border);border-radius:8px;margin-bottom:8px">
    <span style="color:var(--primary-light)">◈</span>
    <b>Projects Root:</b> <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem">{p_dir}</span>
</div>
<div class="terminal-line" style="border:1px solid var(--border);border-radius:8px;margin-bottom:8px">
    <span style="color:var(--primary-light)">◈</span>
    <b>Generated Projects:</b> <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem">{total_projects} projects ({total_size_mb} MB)</span>
</div>
<div class="terminal-line" style="border:1px solid var(--border);border-radius:8px;margin-bottom:8px">
    <span style="color:var(--primary-light)">◈</span>
    <b>Persistent DB:</b> <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem">titan_memory.db (SQLModel / SQLite)</span>
</div>
""",
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div style="text-align:center;padding:2.5rem 0 1rem;border-top:1px solid rgba(255,255,255,0.06);margin-top:3.5rem;font-size:0.75rem;color:var(--text-faint)">
    Project TITAN &nbsp;·&nbsp; Autonomous AI Software Engineering &nbsp;·&nbsp;
    <span style="color:{th['primary_light']};font-family:'JetBrains Mono',monospace">v2.0.0 Enterprise</span>
    &nbsp;·&nbsp;
    <a href="https://github.com/HarshS99/Project_TITAN" target="_blank" style="color:{th['primary']};text-decoration:none">GitHub ↗</a>
</div>
""",
    unsafe_allow_html=True,
)
