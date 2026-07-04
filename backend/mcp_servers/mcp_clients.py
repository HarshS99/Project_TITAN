"""
Agent — Autonomous GitHub Intelligence Agent.
Uses official GitHub MCP Server (v1.1.2) for actions + Groq LLaMA for reasoning.
Supports two modes:
  1. Action Mode — MCP tools (create repo, issues, PRs, branches, etc.)
  2. Analysis Mode — Deep repo/profile analysis via GitHub API + ScrapeGraphAI

Uses a manual tool-calling loop with llm.bind_tools() — no prebuilt agent needed.
"""

import os
import json
import asyncio
import threading
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# ── Safely apply nest_asyncio (skip if uvloop is active) ────────────
try:
    import nest_asyncio
    try:
        # Prefer the currently running loop if available
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop: create and set a new one for compatibility
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Apply nest_asyncio to the loop to allow nested event loops (safe no-op if already applied)
    try:
        nest_asyncio.apply(loop)
    except Exception:
        # If applying fails for any reason (uvloop, unsupported loop), skip gracefully
        pass
except Exception:
    pass  # uvloop or no running loop — skip patching

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import tool
from langchain.agents import create_agent

try:
    from scrapegraph_py import Client as ScrapeClient
    _SCRAPEGRAPH_AVAILABLE = True
except ImportError:
    _SCRAPEGRAPH_AVAILABLE = False

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")

# Load MCP configuration from Config.json (adapted from mcp.json)
MCP_SERVER_TYPE = "stdio"
MCP_COMMAND = None
MCP_ARGS = []
MCP_ENV = os.environ.copy()
MCP_URL = None
MCP_HEADERS = {}

config_path = Path(__file__).parent / "Config.json"
if config_path.is_file():
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        
        # Support {"mcpServers": {"github": ...}}, {"mcp": {"servers": {"github": ...}}}, or {"servers": {"github": ...}}
        github_cfg = cfg.get("mcpServers", {}).get("github")
        if not github_cfg:
            github_cfg = cfg.get("mcp", {}).get("servers", {}).get("github")
        if not github_cfg:
            github_cfg = cfg.get("servers", {}).get("github", {})
            
        MCP_SERVER_TYPE = github_cfg.get("type", "stdio")
        
        if MCP_SERVER_TYPE == "http":
            MCP_URL = github_cfg.get("url")
            headers = github_cfg.get("headers", {})
            for k, v in headers.items():
                if "${input:github_mcp_pat}" in v:
                    v = v.replace("${input:github_mcp_pat}", GITHUB_TOKEN)
                MCP_HEADERS[k] = v
        else:
            MCP_COMMAND = github_cfg.get("command")
            MCP_ARGS = github_cfg.get("args", [])
            for k, v in github_cfg.get("env", {}).items():
                if v == "<YOUR_TOKEN>":
                    v = GITHUB_TOKEN
                MCP_ENV[k] = v
    except Exception as e:
        print(f"[agent] Failed to load Config.json: {e}")

# Inject multiple token formats as requested
if GITHUB_TOKEN:
    for key in [
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GITHUB_LOGIN",
        "GITHUB_TOKEN",
        "GITHUB_AUTH",
        "GITHUB_ACCESS_TOKEN",
        "GITHUB_AUTH_TOKEN",
        "GITHUB_PAT"
    ]:
        MCP_ENV[key] = GITHUB_TOKEN

# Fallback to binary in project root
if MCP_SERVER_TYPE == "stdio" and not MCP_COMMAND:
    default_binary = Path(__file__).parent / "github-mcp-server"
    if default_binary.is_file():
        MCP_COMMAND = str(default_binary)
        MCP_ARGS = ["stdio", "--toolsets", "all"]
    else:
        MCP_COMMAND = None


# ── LLM with smart provider fallback ────────────────────────────────
def _get_llm():
    """Create LLM: Gemini primary (larger quota), Groq as fallback."""
    gemini_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    if gemini_key:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0,
                convert_system_message_to_human=True,
            )
        except Exception:
            pass  # Fall through to Groq
    # Fallback: Groq
    key = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=key,
        temperature=0,
    )


# ── Custom Tools ─────────────────────────────────────────────────────
@tool
def scrape_website(url: str, prompt: str) -> str:
    """Scrape a website using ScrapeGraphAI and return extracted data based on the prompt."""
    if not _SCRAPEGRAPH_AVAILABLE:
        return "Error: scrapegraph_py package is not installed."
    api_key = os.environ.get("SCRAPEGRAPH_API_KEY", "")
    if not api_key:
        return "Error: SCRAPEGRAPH_API_KEY is not set."
    try:
        client = ScrapeClient.from_env()
        res = client.smartscraper(website_url=url, user_prompt=prompt)
        if getattr(res, "status", None) == "success":
            return json.dumps(res.data.json_data, indent=2)
        else:
            return f"Error: {getattr(res, 'error', 'unknown error')}"
    except Exception as e:
        return f"Error scraping website: {e}"


@tool
def extract_documentation(url: str) -> str:
    """Extract full documentation (README, wiki, docs) from a GitHub repo or library URL."""
    prompt = (
        "Extract the complete documentation from the given URL, including README, "
        "any markdown files, and relevant docs. Return the result as formatted markdown."
    )
    return scrape_website.invoke({"url": url, "prompt": prompt})

# ── MCP Tool Filter ──────────────────────────────────────────────────
ESSENTIAL_TOOL_NAMES = {
    "create_repository",
    "get_file_contents",
    "create_or_update_file",
    "push_files",
    "create_pull_request",
    "create_branch",
    "list_branches",
    "list_issues",
    "issue_write",
    "get_me",
    "create_issue",
    "get_repository",
    "search_repositories",
    "search_code",
    "list_commits",
    "list_pull_requests",
    "pull_request_read",
}


def _filter_tools(tools: list) -> list:
    """Keep only essential tools to stay within Groq's TPM limit."""
    filtered = [t for t in tools if t.name in ESSENTIAL_TOOL_NAMES]
    if not filtered:
        print("[agent] Warning: no essential tools matched — returning all MCP tools.")
        return tools
    return filtered


def _trim_tool_descriptions(tools: list, max_chars: int = 120) -> list:
    """Truncate tool descriptions to reduce token count for Groq's TPM limit."""
    for t in tools:
        if hasattr(t, 'description') and t.description and len(t.description) > max_chars:
            t.description = t.description[:max_chars].rstrip() + "…"
    return tools


# ── Action Mode (MCP Tools) ─────────────────────────────────────────
MAX_RETRIES = 5
RETRY_BASE_DELAY = 30  # seconds

async def run_action_async(query: str, system_prompt_override: str = None) -> str:
    """Execute GitHub actions via official MCP Server tools with auto-retry on rate limits."""
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            from contextlib import asynccontextmanager

            @asynccontextmanager
            async def _connect_mcp():
                if MCP_SERVER_TYPE == "http":
                    if not MCP_URL:
                        raise ValueError("HTTP MCP URL not specified in config.")
                    async with sse_client(url=MCP_URL, headers=MCP_HEADERS) as (read, write):
                        yield read, write
                else:
                    if not MCP_COMMAND:
                        raise ValueError(
                            "MCP configuration not found or binary missing.\n"
                            "Please provide a valid `Config.json` or place the `github-mcp-server` binary "
                            "in the project root directory."
                        )
                    server_params = StdioServerParameters(
                        command=MCP_COMMAND,
                        args=MCP_ARGS,
                        env=MCP_ENV
                    )
                    async with stdio_client(server_params) as (read, write):
                        yield read, write

            llm = _get_llm()

            async with _connect_mcp() as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Get tools
                    tools = await load_mcp_tools(session)

                    if not tools:
                        return "❌ No MCP tools loaded. Check the github-mcp-server binary."

                    filtered = _filter_tools(tools)
                    filtered = filtered + [scrape_website, extract_documentation]

                    # Trim descriptions to save tokens
                    _trim_tool_descriptions(filtered)

                    # Enable graceful error handling for all tools so agent can recover from ToolExceptions
                    for t in filtered:
                        t.handle_tool_error = True

                    if system_prompt_override:
                        system_prompt = system_prompt_override
                    else:
                        system_prompt = (
                            "You are an autonomous GitHub assistant focused on repository automation.\n"
                            "Use the provided MCP tools to create repositories, manage branches, open issues, "
                            "submit pull requests, and edit files.\n"
                            "When invoking tools, respect the exact argument names and types. "
                            "CRITICAL: NEVER include extra arguments not defined in the tool's schema (e.g. NEVER add a 'method' parameter). "
                            "CRITICAL: Do NOT pass 'null' or 'None' for optional parameters. If you don't have a value for an optional parameter, OMIT it completely from the tool call.\n"
                            "CRITICAL: Do NOT try to use a 'list_files' tool. It does not exist! If you need to find files, use 'search_code' instead.\n"
                            "Provide concise, actionable responses."
                        )

                    agent = create_agent(
                        model=llm,
                        tools=filtered,
                        system_prompt=system_prompt,
                    )

                    response = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
                    
                    # Get the last message content
                    if "messages" in response and len(response["messages"]) > 0:
                        content = response["messages"][-1].content
                        if isinstance(content, list):
                            text_blocks = [block["text"] for block in content if isinstance(block, dict) and "text" in block]
                            if text_blocks:
                                return "\n".join(text_blocks)
                            return str(content)
                        return str(content)
                    return "✅ Done (no further output)."

        except FileNotFoundError:
            return (
                "❌ `github-mcp-server` binary not found.\n"
                "Download it from: https://github.com/github/github-mcp-server/releases\n"
                "Place it in the project root directory."
            )
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()

            # Check if it's a rate-limit error
            is_rate_limit = (
                "RateLimitError" in tb_str
                or "429" in tb_str
                or "rate_limit" in tb_str.lower()
            )

            if is_rate_limit and attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * attempt
                print(f"[agent] Rate limited (attempt {attempt}/{MAX_RETRIES}). Retrying in {delay}s...")
                await asyncio.sleep(delay)
                last_error = tb_str
                continue

            if is_rate_limit:
                return (
                    f"⏳ **Rate Limited** — Groq's free tier limits requests. "
                    f"Retried {MAX_RETRIES} times but still rate-limited. "
                    f"Please wait ~60 seconds and try again."
                )

            if "tool_use_failed" in tb_str or "BadRequestError" in tb_str:
                import re
                m = re.search(r"'failed_generation':\s*'(.*?)'", tb_str, re.DOTALL)
                if m:
                    failed = m.group(1)
                    return (
                        f"⚠️ **Groq Tool Validation Error**\n\n"
                        f"The Groq API rejected the tool call because of strict schema validation (e.g., passing `null` for omitted arguments).\n\n"
                        f"AI Attempt:\n```\n{failed}\n```\n\n"
                        f"Please try again or refine your prompt."
                    )
            return f"❌ **Agent Error**\n```\n{tb_str}```"

    # Should not reach here, but just in case
    return f"❌ **Agent Error** — All {MAX_RETRIES} retry attempts failed.\n```\n{last_error}\n```"


def _run_in_new_loop(coro):
    """Run an async coroutine in a fresh event loop on a new thread.
    This avoids conflicts with Streamlit's uvloop."""
    result = [None]
    exc = [None]

    def _target():
        try:
            result[0] = asyncio.run(coro)
        except Exception as e:
            exc[0] = e

    t = threading.Thread(target=_target)
    t.start()
    t.join()

    if exc[0] is not None:
        raise exc[0]
    return result[0]


def run_action(query: str, system_prompt_override: str = None) -> str:
    """Sync wrapper for action mode. Works inside Streamlit (uvloop)."""
    return _run_in_new_loop(run_action_async(query, system_prompt_override))


# ── Project TITAN Integration Wrapper ───────────────────────────────────────
def run_push(project_root: str, repo_name: str, description: str = "",
             private: bool = False, branches: list[str] | None = None) -> dict:
    """
    Adapter for TITAN's Phase 5 orchestrator. Creates the repo via GitHub REST API
    (bypassing LLMs for speed and 100% reliability), then performs local git init 
    and pushes via CLI.
    """
    import requests
    import subprocess
    import git
    from backend.config import GITHUB_USERNAME
    
    branches = branches or ["main"]
    result = {"success": False, "repo_url": "", "errors": []}
    root = Path(project_root)
    
    if not GITHUB_TOKEN:
        result["errors"].append("GITHUB_PERSONAL_ACCESS_TOKEN is missing.")
        return result

    # 1. Local git init and commit
    try:
        if (root / ".git").exists():
            repo = git.Repo(root)
        else:
            repo = git.Repo.init(root)

        repo.git.add(A=True)
        try:
            repo.head.commit
        except Exception:
            repo.index.commit(f"🤖 {repo_name} — Generated by Project TITAN")
    except Exception as e:
        result["errors"].append(f"git init/commit failed: {e}")
        return result

    # 2. Create the GitHub Repository via REST API (Ultra-fast, zero AI tokens)
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False
    }
    
    print(f"[GitHub API] Creating repository '{repo_name}'...")
    res = requests.post("https://api.github.com/user/repos", json=payload, headers=headers)
    
    if res.status_code in (201, 200):
        repo_data = res.json()
        result["repo_url"] = repo_data.get("clone_url")
    elif res.status_code == 422: # Repo already exists
        print(f"[GitHub API] Repository '{repo_name}' already exists. Attempting to fetch URL...")
        # Fetch the existing repo URL
        username = GITHUB_USERNAME or "HarshS99"
        get_res = requests.get(f"https://api.github.com/repos/{username}/{repo_name}", headers=headers)
        if get_res.status_code == 200:
            result["repo_url"] = get_res.json().get("clone_url")
        else:
            result["errors"].append(f"Repo exists but could not fetch it: {get_res.text}")
            return result
    else:
        result["errors"].append(f"GitHub API Error {res.status_code}: {res.text}")
        return result

    if not result["repo_url"]:
        result["errors"].append("Could not retrieve clone URL from GitHub API.")
        return result

    # 3. Push code to the new repository via subprocess (token auth)
    try:
        username = GITHUB_USERNAME or "HarshS99"
        # Format push URL with token for auth
        push_url = result["repo_url"].replace("https://", f"https://{username}:{GITHUB_TOKEN}@")
        
        try:
            origin = repo.remote("origin")
            origin.set_url(push_url)
        except ValueError:
            repo.create_remote("origin", push_url)

        try:
            if repo.active_branch.name != "main":
                repo.git.branch("-M", "main")
        except Exception:
            pass

        cmd = "git push -u origin main --force"
        print(f"[GitHub Push] Pushing to {result['repo_url']}...")
        proc = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
        
        if proc.returncode == 0:
            result["success"] = True
            print("[GitHub Push] Successfully pushed code to GitHub!")
        else:
            result["errors"].append(f"git push failed: {proc.stderr}")
    except Exception as e:
        result["errors"].append(f"Push failed: {e}")

    return result