# ⚡ Project TITAN

<div align="center">

![TITAN Banner](https://img.shields.io/badge/Project-TITAN-6366f1?style=for-the-badge&logo=robot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CAMEL AI](https://img.shields.io/badge/CAMEL-AI-FF6B6B?style=for-the-badge)
![MCP Server](https://img.shields.io/badge/MCP-Server-0D9488?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F54E00?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-4ade80?style=for-the-badge)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)

**The world's first open-source AI Desktop Commander.**
Built with CAMEL AI orchestration and an MCP Server for autonomous GitHub workflows.
Type a project idea. Watch it get planned, coded, tested, and pushed to GitHub — automatically.

[🚀 Quick Start](#-quick-start) · [📖 How It Works](#-how-it-works) · [🎯 Features](#-features) · [🗺️ Roadmap](#️-roadmap) · [🤝 Contributing](#-contributing)

</div>

---

## 📑 Table of Contents

- [What is Project TITAN?](#-what-is-project-titan)
- [Features](#-features)
- [Architecture](#️-architecture)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [AI Models](#-ai-models)
- [Configuration Reference](#️-configuration-reference)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 What is Project TITAN?

Project TITAN is an **autonomous AI software engineering system** that orchestrates multiple specialized AI agents to build complete software projects from a single prompt — no scaffolding, no boilerplate hunting, no manual repo setup.

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

You don't touch anything — TITAN plans, writes, tests, documents, and ships the project end-to-end.

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
┌─────────────────────────▼────────────────────────────────┐
│                   FASTAPI BACKEND                         │
│              /build  /status  /projects                   │
└─────────────────────────┬───────────────────────────────-┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│                    ORCHESTRATOR                            │
│         The master brain — coordinates everything          │
└──┬──────────┬──────────┬──────────┬────────────┬─────────┘
   │          │          │          │            │
   ▼          ▼          ▼          ▼            ▼
Planner    Code       Testing    Docs        GitHub
Agent      Agent      Agent      Agent       Controller
(Groq)     (Groq)     (Groq)     (Groq)     (PyGithub)
   │                                            │
   └─────────────── CAMEL AI ──────────────────┘
```

---

## 🔄 How It Works

1. **Describe your project** in plain English through the dashboard, API, or Python SDK.
2. **Planner Agent** decomposes the request into an ordered task graph (models, endpoints, tests, docs, deployment).
3. **Code Agent** writes each file per the plan, respecting project conventions and dependencies.
4. **Testing Agent** runs the project, catches failures, and iterates on fixes until things pass.
5. **Docs Agent** generates a README, `.gitignore`, `LICENSE`, and optional CI/CD config.
6. **GitHub Controller** initializes the repo, commits with meaningful messages, pushes, and cuts a release.
7. **VS Code Controller** opens the finished project locally so you can dive straight in.

Every step streams live to the dashboard so you can watch each agent's reasoning and output as it happens.

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

You can add Gemini or Mistral API keys to `.env` to enable those providers too, then set `model_router` preferences per agent.

---

## ⚙️ Configuration Reference

| Variable | Required | Description |
|----------|----------|--------------|
| `GROQ_API_KEY` | ✅ | Powers all four agents by default |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | ✅ | Needs `repo` scope for repo creation, commits, and releases |
| `SCRAPEGRAPH_API_KEY` | ❌ | Enables web research for agents that need up-to-date context |
| `GEMINI_API_KEY` | ❌ | Optional alternate model provider |
| `MISTRAL_API_KEY` | ❌ | Optional alternate model provider |

---

## 🛠 Troubleshooting

- **Backend won't start** — confirm `GROQ_API_KEY` is set in `.env` and the virtual environment is activated.
- **GitHub push fails** — verify your PAT has `repo` scope and hasn't expired.
- **VS Code doesn't open automatically** — make sure the `code` CLI command is on your `PATH` (Command Palette → "Shell Command: Install 'code' command in PATH").
- **Dashboard shows no activity** — check that the FastAPI backend (Terminal 1) is running before launching Streamlit.

---

## 🗺️ Roadmap

- [ ] Multi-language support beyond Python (Node.js, Go)
- [ ] Pluggable agent framework for custom workflows
- [ ] Docker Compose one-command launch
- [ ] Built-in deployment targets (Vercel, Railway, Fly.io)
- [ ] Fine-grained per-agent model selection in the dashboard

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repo and create a feature branch.
2. Make your changes with clear, focused commits.
3. Open a pull request describing what you changed and why.

Please open an issue first for larger changes so we can discuss the approach.

---

## 📜 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built with ❤️ using CAMEL AI, Groq, FastAPI, and Streamlit**

⭐ Star this repo if TITAN helped you build something amazing!

</div>
