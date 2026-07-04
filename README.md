# ⚡ Project TITAN

<div align="center">

![TITAN Banner](https://img.shields.io/badge/Project-TITAN-6366f1?style=for-the-badge&logo=robot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CAMEL AI](https://img.shields.io/badge/CAMEL-AI-FF6B6B?style=for-the-badge)
![MCP Server](https://img.shields.io/badge/MCP-Server-0D9488?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F54E00?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-4ade80?style=for-the-badge)

**The world's first open-source AI Desktop Commander.**
Built with CAMEL AI orchestration and an MCP Server for autonomous GitHub workflows.
Type a project idea. Watch it get planned, coded, tested, and pushed to GitHub — automatically.

[🚀 Quick Start](#-quick-start) · [📖 Documentation](#-how-it-works) · [🎯 Features](#-features)

</div>

---

## 🌟 What is Project TITAN?

Project TITAN is an **autonomous AI software engineering system** that orchestrates multiple specialized AI agents to build complete software projects from a single prompt.

```
You type:  "Build me a FastAPI Todo API with authentication"

TITAN does:
  🧠 Planner  →  Breaks into 25 ordered tasks
  💻 Code     →  Writes all Python files, configs, tests
  🧪 Testing  →  Detects & fixes any errors automatically
  📚 Docs     →  Generates README, .gitignore, LICENSE
  🌿 GitHub   →  Creates repo, commits, pushes, makes release
  🔵 VS Code  →  Opens project automatically
```

You don't touch anything.

---

## ✨ Features

| Module | Capabilities |
|--------|-------------|
| 🧠 **Planner Agent** | Breaks any project into ordered, structured tasks |
| 💻 **Code Agent** | Writes complete, production-ready files |
| 🧪 **Testing Agent** | Diagnoses errors and iteratively fixes them |
| 📚 **Docs Agent** | Generates README, .gitignore, LICENSE, CI/CD |
| 🌿 **GitHub Controller** | Creates repos, branches, commits, pushes, releases |
| 📂 **File System Controller** | Safe, sandboxed file & folder operations |
| 🖥️ **Terminal Controller** | Runs commands with streaming output |
| 🔵 **VS Code Controller** | Opens project in VS Code automatically |
| 🧠 **Session Memory** | SQLite-based persistent project & task history |
| ⚡ **FastAPI Backend** | REST API with real-time progress streaming |
| 🎨 **Streamlit Dashboard** | Stunning real-time command center UI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT DASHBOARD                    │
│              (Real-time agent activity feed)             │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│                   FASTAPI BACKEND                        │
│              /build  /status  /projects                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    ORCHESTRATOR                          │
│         The master brain — coordinates everything        │
└──┬──────────┬──────────┬──────────┬────────────┬────────┘
   │          │          │          │            │
   ▼          ▼          ▼          ▼            ▼
Planner    Code       Testing    Docs        GitHub
Agent      Agent      Agent      Agent       Controller
(Groq)     (Groq)     (Groq)     (Groq)     (PyGithub)
   │                                            │
   └─────────────── CAMEL AI ──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- GitHub CLI (`gh`) — optional but recommended
- VS Code — optional

### 1. Clone & Setup

```bash
cd Project_TITAN
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Edit .env with your keys
cp .env.example .env
```

Required:
- `GROQ_API_KEY` — [Get free at console.groq.com](https://console.groq.com)
- `GITHUB_PERSONAL_ACCESS_TOKEN` — [Create at github.com/settings/tokens](https://github.com/settings/tokens) (needs `repo` scope)

Optional:
- `SCRAPEGRAPH_API_KEY` — For web research capabilities

### 3. Launch TITAN

**Terminal 1 — Start the backend:**
```bash
python -m backend.main
```

**Terminal 2 — Start the dashboard:**
```bash
streamlit run ui/app.py
```

Open [http://localhost:8501](http://localhost:8501) and start building! 🚀

---

## 🎮 Usage

### Via Dashboard
1. Open `http://localhost:8501`
2. Type your project idea
3. Adjust settings (GitHub push, VS Code, private repo)
4. Click **🚀 LAUNCH TITAN**
5. Watch it build in real-time

### Via API

```bash
# Start a build
curl -X POST http://localhost:8000/build \
  -H "Content-Type: application/json" \
  -d '{"request": "Build a Flask blog with user authentication"}'

# Check status
curl http://localhost:8000/build/{build_id}

# List all projects
curl http://localhost:8000/projects
```

### Via Python

```python
from backend.orchestrator import Orchestrator

def on_progress(event):
    print(f"[{event.agent}] {event.action}: {event.message}")

orchestrator = Orchestrator(on_progress=on_progress)
result = orchestrator.build("Build a FastAPI todo API")

print(f"✅ Built: {result.project_name}")
print(f"🌿 GitHub: {result.github_url}")
```

---

## 📁 Project Structure

```
Project_TITAN/
├── .env                    ← Your API keys
├── .env.example            ← Template
├── requirements.txt        ← Dependencies
├── README.md
│
├── backend/
│   ├── main.py             ← FastAPI server
│   ├── orchestrator.py     ← Master controller
│   ├── config.py           ← Configuration
│   │
│   ├── ai/
│   │   └── model_router.py ← Routes to AI providers
│   │
│   ├── agents/
│   │   ├── planner_agent.py   ← Breaks projects into tasks
│   │   ├── code_agent.py      ← Writes code
│   │   ├── testing_agent.py   ← Fixes errors
│   │   └── docs_agent.py      ← Generates docs
│   │
│   ├── controllers/
│   │   ├── filesystem.py   ← File operations
│   │   ├── terminal.py     ← Shell commands
│   │   ├── github.py       ← GitHub automation
│   │   └── vscode.py       ← VS Code control
│   │
│   └── memory/
│       └── session.py      ← SQLite memory
│
├── ui/
│   └── app.py              ← Streamlit dashboard
│
├── projects/               ← Built projects land here
└── logs/                   ← Activity logs
```

---

## 🤖 AI Models

TITAN currently uses **Groq Llama 3.3 70B** for all agents (extremely fast + capable).

| Agent | Model | Role |
|-------|-------|------|
| Planner | Groq Llama 3.3 70B | Project decomposition |
| Code | Groq Llama 3.3 70B | Code generation |
| Testing | Groq Llama 3.3 70B | Error diagnosis & fixing |
| Docs | Groq Llama 3.3 70B | README & documentation |

You can add Gemini or Mistral API keys to `.env` to enable those providers too.

---

## 📜 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built with ❤️ using CAMEL AI, Groq, FastAPI, and Streamlit**

⭐ Star this repo if TITAN helped you build something amazing!

</div>
