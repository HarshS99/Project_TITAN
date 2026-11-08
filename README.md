# ⚡ Project TITAN

<div align="center">

```
  ████████╗ ██╗ ████████╗  █████╗  ███╗   ██╗
  ╚══██╔══╝ ██║ ╚══██╔══╝ ██╔══██╗ ████╗  ██║
     ██║    ██║    ██║    ███████║ ██╔██╗ ██║
     ██║    ██║    ██║    ██╔══██║ ██║╚██╗██║
     ██║    ██║    ██║    ██║  ██║ ██║ ╚████║
     ╚═╝    ╚═╝    ╚═╝    ╚═╝  ╚═╝ ╚═╝  ╚═══╝
  ═══════════════════════════════════════════
   A U T O N O M O U S   A I   F A C T O R Y
```

[![Release](https://img.shields.io/badge/Release-v2.0.0_Enterprise-10B981?style=for-the-badge&logo=rocket&logoColor=white)](https://github.com/HarshS99/Project_TITAN)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CAMEL AI](https://img.shields.io/badge/Orchestration-CAMEL--AI_0.2-FF6B6B?style=for-the-badge&logo=probot&logoColor=white)](https://www.camel-ai.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit_Dark-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MCP Protocol](https://img.shields.io/badge/Protocol-Model_Context_Protocol-0D9488?style=for-the-badge)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](LICENSE)

<br/>

**The Autonomous Multi-Agent Software Factory & Systems Architecture Engine.**  
*Describe any software concept. TITAN's agent mesh plans the architecture, synthesizes production code, executes tests in sandboxed terminals, repairs failures, generates docs, and deploys to GitHub — fully autonomously.*

<br/>

[🌟 3D Architecture](#-3d-system-architecture) • [🔄 Autonomous Loop](#-autonomous-execution-loop) • [✨ Capabilities](#-features--agent-mesh) • [🚀 Quick Start](#-quick-start) • [📡 API Reference](#-rest-api-documentation) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 3D System Architecture

```
                                  ▲
                                 / \
                                /   \
                               /     \
   ┌───────────────────────────┐      ┌───────────────────────────┐
  /   STREAMLIT STUDIO UI     /│     /   FASTAPI EVENT ENGINE    /│
 /  • Interactive Studio     / │    /  • Async Event Stream     / │
/   • Project Explorer      /  │   /   • Health & Model Router /  │
┌───────────────────────────┐  │   ┌───────────────────────────┐  │
│ • Floating Support System │  │   │ • Telemetry / Chat Hub    │  │
│ • Real-time Build Console │ /    │ • Sandboxed Terminal Host │ /
└───────────────────────────┘/     └───────────────────────────┘/
              │                                  │
              ▼                                  ▼
   ╔═══════════════════════════════════════════════════════════════╗
  //                 ORCHESTRATOR EVENT BUS & DAG                 //
 ╔═══════════════════════════════════════════════════════════════╗
//   • Dynamic Task Decomposition & Dependency Resolution        //
╚═══════════════════════════════════════════════════════════════╝
              │                                  │
              ├─────────────────┬────────────────┤
              ▼                 ▼                ▼
   ┌────────────────────┐┌────────────────────┐┌────────────────────┐
  /  🧠 PLANNER AGENT   //  ⚙️ CODE ENGINEER   //  🧪 QA DIAGNOSTIC  /
 /  Gemini 2.5 Flash   //  Groq GPT-OSS 120B  //  Iterative Healing/
/────────────────────//────────────────────//────────────────────/
          │                     │                     │
          ▼                     ▼                     ▼
   ┌────────────────────┐┌────────────────────┐┌────────────────────┐
  /  📝 DOCS AGENT      //  🚀 GITHUB TOOLKIT  //  💾 SQLITE MEMORY  /
 /  Architecture & Spec//  MCP Server Auto-VCS//  SQLModel Telemetry/
/────────────────────//────────────────────//────────────────────/
```

---

## 🔄 Autonomous Execution Loop

TITAN operates on an iterative, closed-loop cybernetic engineering pipeline:

```
                  ┌───────────────────────────────┐
                  │ 💡 Single User Prompt / Spec  │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ 🧠 01. PLANNER AGENT (Gemini 2.5 Flash)                       │
  │     • Deconstructs requirements into Directed Acyclic Graph   │
  │     • Generates strict JSON schemas & file dependencies       │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ ⚙️ 02. CODE ENGINEER (OpenAI GPT-OSS / Gemini)                │
  │     • Zero-placeholder, production code synthesis             │
  │     • AST linting and dependency ordering                     │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ 🧪 03. QA & DIAGNOSTIC AGENT (Terminal Sandbox)               │
  │     • Executes automated unit tests & syntax checks           │
  │     • Diagnoses tracebacks and applies in-place self-healing  │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ 📝 04. DOCUMENTATION AGENT (CAMEL AI Agent)                   │
  │     • Synthesizes comprehensive architectural READMEs         │
  │     • Generates .gitignore, LICENSE, and CI/CD workflows      │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ 🚀 05. VCS & REPOSITORY CONTROLLER (GitHub MCP Toolkit)       │
  │     • Initializes Git repo, sets branch topologies            │
  │     • Pushes atomic commits and triggers remote releases      │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │ 🎉 Verified Shipped Software! │
                  └───────────────────────────────┘
```

---

## ✨ Features & Agent Mesh

| Component | Architecture & Tech | Role & Capabilities |
| :--- | :--- | :--- |
| **🧠 Planner Agent** | Gemini 2.5 Flash / CAMEL | Deconstructs free-form specs into a validated, dependency-ordered micro-task tree. |
| **⚙️ Code Engineer** | Groq `openai/gpt-oss-120b` | Synthesizes complete, modular code files with strict types, schemas, and zero placeholders. |
| **🧪 QA Diagnostic Tester** | Terminal Subprocess + Gemini | Runs test suites, captures stderr tracebacks, and iteratively rewrites code to fix bugs. |
| **📝 Documentation Agent** | CAMEL AI Docs Specialist | Generates production documentation, architecture guides, and API manifests. |
| **🚀 GitHub MCP Server** | Model Context Protocol / FastMCP | Automates repository initialization, staging, branch creation, commits, and remote pushing. |
| **🎧 Support System Widget** | Floating Circular Widget UI | 24/7 in-app architecture copilot, live prompt architect, and instant systems diagnostics. |
| **📁 Project Explorer** | Streamlit Code Studio | Live multi-project tree navigator, syntax-highlighted code inspector, and ZIP exporter. |
| **💾 Session Memory** | SQLModel + SQLite 3 | Tracks project builds, error records, agent decisions, and historical build graphs. |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Git CLI
- VS Code (optional, for automatic workspace launching)

### 2. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/HarshS99/Project_TITAN.git
cd Project_TITAN

# Create an isolated virtual environment (bypassing macOS iCloud sync)
python3 -m venv venv.nosync
ln -s venv.nosync venv
source venv/bin/activate

# Install locked dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials
Create `.env` in the root directory:
```bash
cp .env.example .env
```

Add your API keys:
```env
# Primary Fast Inference Provider (Groq)
GROQ_API_KEY="gsk_..."

# Google Gemini API (Planning & Diagnosis)
GEMINI_API_KEY="AIzaSy..."

# GitHub Personal Access Token (repo scope for automated push)
GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."

# Optional Providers
MISTRAL_API_KEY="mis_..."
```

### 4. Launch the Systems Factory

**Terminal 1 — Launch FastAPI Engine (Port 8000):**
```bash
source venv/bin/activate
python -m backend.main
```

**Terminal 2 — Launch Streamlit Console (Port 8501):**
```bash
source venv/bin/activate
streamlit run ui/app.py
```

Open your browser at **[http://localhost:8501](http://localhost:8501)** to access the TITAN Console.

---

## 🎮 Usage & Examples

### 1. Web Console Build
1. Open the **Command Center** in the Streamlit UI.
2. Enter your specification (e.g., *"Build an asynchronous webhook routing service in FastAPI with SQLite persistence and JWT auth"*).
3. Optionally click **✨ AI Prompt Architect** to automatically expand your idea into a production specification.
4. Click **⚡ Launch Autonomous Build** and watch the agents build the project in real time.

### 2. Programmatic Python SDK
```python
from backend.orchestrator import Orchestrator

def progress_hook(event):
    print(f"[{event.agent.upper()}] {event.action}: {event.message}")

orchestrator = Orchestrator(on_progress=progress_hook)
result = orchestrator.build(
    "Build a production Redis cache proxy with token-bucket rate limiting"
)

if result.success:
    print(f"✅ Build Completed: {result.project_name}")
    print(f"🌿 GitHub URL: {result.github_url}")
```

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Live status of the backend, active model providers, and project directories. |
| `POST` | `/build` | Triggers a full autonomous software build with asynchronous worker task. |
| `GET` | `/build/{id}` | Polls status, completed tasks count, and execution errors. |
| `GET` | `/build/{id}/events` | SSE event stream delivering real-time agent output logs. |
| `POST` | `/prompt/enhance` | Invokes the AI Systems Architect to expand short concepts into production specifications. |
| `POST` | `/chat` | Live messaging endpoint powering the floating **Support System** assistant. |
| `GET` | `/projects` | Lists all historical builds, completion rates, and VCS links. |
| `GET` | `/projects/{name}/files` | Lists all source and config files in a built project workspace. |
| `GET` | `/projects/{name}/file` | Fetches the raw content of any file inside a project. |
| `POST` | `/projects/{name}/open_vscode` | Triggers the VS Code controller to launch the project locally. |
| `GET` | `/system/ping_providers` | Live round-trip latency benchmarks for Groq, Gemini, and Mistral. |

---

## 📁 Repository Structure

```
Project_TITAN/
├── .env.example                     ← Template for API keys
├── requirements.txt                 ← Pinned production dependencies
├── titan_memory.db                  ← SQLite persistent build database
├── README.md                        ← 3D Architecture & Documentation
│
├── backend/
│   ├── main.py                      ← FastAPI server with event streaming & REST endpoints
│   ├── orchestrator.py              ← Central controller coordinating the multi-agent DAG
│   ├── config.py                    ← Configuration & environment loader
│   │
│   ├── agents/
│   │   ├── planner_agent.py         ← DAG task planner (Gemini 2.5 Flash)
│   │   ├── code_agent.py            ← Code synthesis engine (Groq GPT-OSS 120B)
│   │   ├── testing_agent.py         ← Diagnostic QA tester with self-healing feedback
│   │   └── docs_agent.py            ← Technical documentation & README generator
│   │
│   ├── ai/
│   │   └── model_factory.py         ← Unified LLM routing (Groq, Gemini, Mistral)
│   │
│   ├── controllers/
│   │   ├── filesystem.py            ← Sandboxed file operations
│   │   ├── terminal.py              ← Subprocess command execution engine
│   │   ├── github.py                ← PyGithub automation (branches, repos, releases)
│   │   └── vscode.py                ← Local IDE automation
│   │
│   ├── mcp_servers/
│   │   ├── github_mcp_server.py     ← Model Context Protocol GitHub server
│   │   └── mcp_clients.py           ← LangChain & CAMEL MCP bridge
│   │
│   └── memory/
│       └── session.py               ← SQLModel persistent project & task history
│
├── ui/
│   └── app.py                       ← Enterprise Streamlit console & Support System widget
│
└── projects/                        ← Generated production software repositories
```

---

## 🛠️ Diagnostics & Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `Backend Standby (Port 8000)` | Backend daemon not started | Run `python -m backend.main` in a separate terminal. |
| `Missing Provider Keys` | Unconfigured `.env` variables | Verify `GROQ_API_KEY` and `GEMINI_API_KEY` in `.env`. |
| `GitHub Push 401 Unauthorized` | Invalid or expired token | Ensure your GitHub PAT has `repo`, `workflow`, and `read:org` scopes. |
| `iCloud FileProvider Sync Error` | macOS iCloud offloading files | Use `venv.nosync/` virtual environment to prevent eviction. |
| `VS Code CLI not found` | `code` binary not on PATH | In VS Code, run `CMD+Shift+P` → *Shell Command: Install 'code' command in PATH*. |

---

## 🤝 Contributing

Contributions are warmly welcomed!

1. Fork the Project TITAN repository.
2. Create your feature branch (`git checkout -b feat/quantum-compiler`).
3. Commit your changes with conventional commit messages (`git commit -m "feat: add AST type validator"`).
4. Push to the branch (`git push origin feat/quantum-compiler`).
5. Open a Pull Request.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<div align="center">

**Built with ⚡ by [Harsh Singh](https://github.com/HarshS99) and the open-source community.**

⭐ **Star this repository if Project TITAN helped you ship faster!**

</div>
