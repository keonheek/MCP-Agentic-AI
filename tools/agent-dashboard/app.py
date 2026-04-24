"""
Agent Dashboard — Keonhee's HQ
Shows task, status, and color per agent. Polls agents/status.json every 3s.

Status colors:
  green  (#00CC44) — working
  red    (#FF3355) — needs human action
  gray   (#555566) — idle / not running
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

import streamlit as st

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent
STATUS_FILE   = _PROJECT_ROOT / "agents" / "status.json"
REGISTRY_FILE = _PROJECT_ROOT / "tasks" / "orchestrator_registry.json"

# ---------------------------------------------------------------------------
# Agent config
# ---------------------------------------------------------------------------
AGENTS = [
    {"name": "GEO",        "icon": "🌐", "project": "geo-agency"},
    {"name": "Lead Intel", "icon": "🔍", "project": "lead-intelligence"},
    {"name": "SME Diag",   "icon": "🏭", "project": "sme-diagnostic-ai"},
    {"name": "Consulting", "icon": "📊", "project": "consulting-emulation"},
    {"name": "Next Role",  "icon": "🎯", "project": "next-ai-role"},
    {"name": "Discord Bot","icon": "💬", "project": "tools/discord-bot"},
    {"name": "Claude Loop", "icon": "⚙️",  "project": "loop"},
]

# Status → color + label
STATUS_CONFIG = {
    "working": {"color": "#00CC44", "label": "● WORKING",      "dot": "#00CC44"},
    "blocked": {"color": "#FF3355", "label": "⚠ NEEDS ACTION", "dot": "#FF3355"},
    "idle":    {"color": "#555566", "label": "○ IDLE",          "dot": "#555566"},
    "done":    {"color": "#00CC44", "label": "✓ DONE",          "dot": "#00CC44"},
}
DEFAULT_CONFIG = STATUS_CONFIG["idle"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_status() -> dict:
    if not STATUS_FILE.exists():
        return {}
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_registry() -> dict:
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def pid_alive(pid: int) -> bool:
    """Check if a PID is still running (cross-platform)."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def relative_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = int((datetime.now() - dt).total_seconds())
        if diff < 10:   return "just now"
        if diff < 60:   return f"{diff}s ago"
        if diff < 3600: return f"{diff // 60}m ago"
        return f"{diff // 3600}h ago"
    except Exception:
        return "—"


def render_card(agent: dict, agent_status: dict) -> None:
    status  = agent_status.get("status", "idle")
    task    = agent_status.get("task", "Not running")
    updated = agent_status.get("updated_at", "")

    cfg      = STATUS_CONFIG.get(status, DEFAULT_CONFIG)
    color    = cfg["color"]
    label    = cfg["label"]
    time_ago = relative_time(updated) if updated else "—"

    # Glow only for active states
    glow = f"0 0 12px {color}55" if status in ("working", "blocked") else "none"

    st.markdown(f"""
    <div style="
        background: #141420;
        border: 2px solid {color};
        border-radius: 6px;
        padding: 18px 20px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
        box-shadow: {glow};
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:1.05em; color:#ffffff; font-weight:bold; letter-spacing:0.5px;">
                {agent['icon']}&nbsp;&nbsp;{agent['name']}
            </span>
            <span style="
                background:{color}1a;
                color:{color};
                border:1.5px solid {color};
                border-radius:3px;
                padding:3px 10px;
                font-size:0.72em;
                font-weight:bold;
                letter-spacing:1.5px;
            ">{label}</span>
        </div>
        <div style="
            color:#ccccdd;
            font-size:0.88em;
            line-height:1.5;
            margin-bottom:8px;
            min-height:1.4em;
        ">{task}</div>
        <div style="color:#44445a; font-size:0.72em;">
            {agent['project']} &nbsp;·&nbsp; {time_ago}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Keonhee HQ", page_icon="🖥️", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0a0a14; }
    .block-container { padding-top: 2rem; max-width: 620px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("## 🖥️ KEONHEE HQ")

status_data = load_status()

working = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "working")
blocked = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "blocked")
idle    = len(AGENTS) - working - blocked

st.markdown(f"""
<div style="
    background:#0f0f1e;
    border:1px solid #222233;
    border-radius:5px;
    padding:10px 18px;
    margin-bottom:1.5rem;
    font-family:monospace;
    font-size:0.82em;
    display:flex;
    gap:20px;
    align-items:center;
">
    <span style="color:#00CC44;">● {working} working</span>
    <span style="color:#FF3355;">⚠ {blocked} blocked</span>
    <span style="color:#555566;">○ {idle} idle</span>
    <span style="margin-left:auto; color:#333344; font-size:0.9em;">↻ 3s</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------
for agent in AGENTS:
    render_card(agent, status_data.get(agent["name"], {}))

# ---------------------------------------------------------------------------
# Orchestrator registry
# ---------------------------------------------------------------------------
registry = load_registry()

st.markdown("---")
st.markdown("""
<div style="font-family:monospace; font-size:0.8em; color:#888899; margin-bottom:0.5rem; letter-spacing:1px;">
    RUNNING ORCHESTRATORS
</div>
""", unsafe_allow_html=True)

if not registry:
    st.markdown("""
    <div style="
        background:#0f0f1e;
        border:1px dashed #222233;
        border-radius:5px;
        padding:10px 16px;
        font-family:monospace;
        font-size:0.82em;
        color:#333344;
        margin-bottom:1rem;
    ">No orchestrators running — start one with:<br>
    <span style="color:#555566;">python tools/orchestrator.py --name "GEO" --command "/execute-next" --interval 300</span>
    </div>
    """, unsafe_allow_html=True)
else:
    for orch_name, info in registry.items():
        alive   = pid_alive(info.get("pid", -1))
        dot_col = "#00CC44" if alive else "#555566"
        label   = "RUNNING" if alive else "DEAD"
        runs    = info.get("runs", 0)
        started = relative_time(info.get("started_at", ""))
        cmd     = info.get("command", "?")
        pid     = info.get("pid", "?")

        st.markdown(f"""
        <div style="
            background:#141420;
            border:1.5px solid {dot_col};
            border-radius:5px;
            padding:10px 16px;
            margin-bottom:8px;
            font-family:monospace;
            font-size:0.82em;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#ffffff; font-weight:bold;">
                    ⚙️&nbsp;&nbsp;{orch_name}
                </span>
                <span style="
                    color:{dot_col};
                    border:1px solid {dot_col};
                    border-radius:3px;
                    padding:2px 8px;
                    font-size:0.72em;
                    letter-spacing:1.5px;
                ">{'●' if alive else '○'} {label}</span>
            </div>
            <div style="color:#888899; margin-top:6px;">
                {runs} runs &nbsp;·&nbsp; cmd: <span style="color:#ccccdd;">{cmd}</span> &nbsp;·&nbsp; started {started}
            </div>
            <div style="color:#333344; font-size:0.9em; margin-top:2px;">PID {pid}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Auto-refresh
# ---------------------------------------------------------------------------
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1
time.sleep(3)
st.rerun()
