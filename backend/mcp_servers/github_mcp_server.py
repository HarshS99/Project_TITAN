"""
GitHub Automation MCP Server
-----------------------------
A Model Context Protocol (MCP) server exposing GitHub automation tools:
repositories, issues, pull requests, branches, files, commits, and search.

Install dependencies:
    pip install "mcp[cli]" requests

Set your token (needed for private repos, write ops, and higher rate limits):
    export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxxxxxxxxxx"

Run directly (stdio transport, for local testing / Claude Desktop, etc.):
    python github_mcp_server.py

Example mcpServers config entry (Claude Desktop / claude_desktop_config.json):
{
  "mcpServers": {
    "github": {
      "command": "python3",
      "args": ["/absolute/path/to/github_mcp_server.py"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
"""

import os
import sys
from typing import Any, Optional

import requests
from mcp.server.fastmcp import FastMCP

GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")

mcp = FastMCP("github-automation")

session = requests.Session()
session.headers.update(
    {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-automation-mcp/1.0",
    }
)
if TOKEN:
    session.headers["Authorization"] = f"Bearer {TOKEN}"


def _request(method: str, path: str, **kwargs) -> Any:
    """Wrapper around requests that raises a readable error for the model."""
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    resp = session.request(method, url, timeout=30, **kwargs)

    if resp.status_code == 401:
        raise RuntimeError(
            "GitHub API returned 401 Unauthorized. Check GITHUB_PERSONAL_ACCESS_TOKEN."
        )
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        raise RuntimeError("GitHub API rate limit exceeded. Add a token or wait and retry.")
    if resp.status_code == 404:
        raise RuntimeError(f"Not found: {url}")
    if not resp.ok:
        raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text[:500]}")
    if resp.status_code == 204 or not resp.content:
        return {"status": "ok"}
    return resp.json()


# ---------------------------------------------------------------------------
# Auth / identity
# ---------------------------------------------------------------------------

@mcp.tool()
def get_me() -> dict:
    """Get the authenticated user's profile (requires a token)."""
    return _request("GET", "/user")


@mcp.tool()
def get_user_profile(username: str) -> dict:
    """Get a GitHub user's public profile (name, bio, followers, company, etc.)."""
    return _request("GET", f"/users/{username}")


@mcp.tool()
def list_user_repos(
    username: str, sort: str = "updated", per_page: int = 30, page: int = 1
) -> list:
    """List public repositories for a GitHub user.

    sort: one of 'created', 'updated', 'pushed', 'full_name'
    """
    return _request(
        "GET",
        f"/users/{username}/repos",
        params={"sort": sort, "per_page": per_page, "page": page},
    )


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

@mcp.tool()
def get_repo(owner: str, repo: str) -> dict:
    """Get details about a specific repository (stars, forks, description, language, etc.)."""
    return _request("GET", f"/repos/{owner}/{repo}")


@mcp.tool()
def create_repository(
    name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = False,
) -> dict:
    """Create a new GitHub repository for the authenticated user. Requires a token."""
    payload = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init,
    }
    return _request("POST", "/user/repos", json=payload)


@mcp.tool()
def search_repositories(query: str, sort: str = "stars", per_page: int = 10) -> dict:
    """Search GitHub repositories.

    query supports GitHub search qualifiers, e.g. 'machine learning language:python stars:>1000'
    sort: 'stars', 'forks', 'updated', or '' for best match
    """
    params = {"q": query, "per_page": per_page}
    if sort:
        params["sort"] = sort
    return _request("GET", "/search/repositories", params=params)


@mcp.tool()
def list_branches(owner: str, repo: str, per_page: int = 30) -> list:
    """List branches in a repository."""
    return _request("GET", f"/repos/{owner}/{repo}/branches", params={"per_page": per_page})


@mcp.tool()
def create_branch(owner: str, repo: str, new_branch: str, from_branch: str = "main") -> dict:
    """Create a new branch in a repository, based off an existing branch (default 'main').
    Requires a token with repo access.
    """
    ref_data = _request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{from_branch}")
    sha = ref_data["object"]["sha"]
    payload = {"ref": f"refs/heads/{new_branch}", "sha": sha}
    return _request("POST", f"/repos/{owner}/{repo}/git/refs", json=payload)


@mcp.tool()
def get_file_contents(owner: str, repo: str, path: str, ref: Optional[str] = None) -> dict:
    """Get the contents of a file or directory listing from a repository."""
    params = {"ref": ref} if ref else {}
    return _request("GET", f"/repos/{owner}/{repo}/contents/{path}", params=params)


@mcp.tool()
def create_or_update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str = "main",
    sha: Optional[str] = None,
) -> dict:
    """Create or update a file in a repository.

    content should be plain text (it will be base64-encoded automatically).
    If updating an existing file, pass its current blob 'sha' (get it via get_file_contents);
    omit sha when creating a new file.
    """
    import base64

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    return _request("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=payload)


@mcp.tool()
def list_commits(
    owner: str, repo: str, branch: Optional[str] = None, per_page: int = 30
) -> list:
    """List recent commits on a repository (optionally on a specific branch)."""
    params = {"per_page": per_page}
    if branch:
        params["sha"] = branch
    return _request("GET", f"/repos/{owner}/{repo}/commits", params=params)


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

@mcp.tool()
def list_issues(
    owner: str, repo: str, state: str = "open", per_page: int = 30, page: int = 1
) -> list:
    """List issues in a repository. state: 'open', 'closed', or 'all'."""
    return _request(
        "GET",
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": per_page, "page": page},
    )


@mcp.tool()
def get_issue(owner: str, repo: str, issue_number: int) -> dict:
    """Get a single issue by number."""
    return _request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")


@mcp.tool()
def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str = "",
    labels: Optional[list[str]] = None,
) -> dict:
    """Create a new issue in a repository. Requires a token with repo access."""
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    return _request("POST", f"/repos/{owner}/{repo}/issues", json=payload)


@mcp.tool()
def add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> dict:
    """Add a comment to an issue or pull request. Requires a token."""
    return _request(
        "POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", json={"body": body}
    )


@mcp.tool()
def close_issue(owner: str, repo: str, issue_number: int) -> dict:
    """Close an open issue. Requires a token."""
    return _request(
        "PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json={"state": "closed"}
    )


# ---------------------------------------------------------------------------
# Pull Requests
# ---------------------------------------------------------------------------

@mcp.tool()
def list_pull_requests(
    owner: str, repo: str, state: str = "open", per_page: int = 30, page: int = 1
) -> list:
    """List pull requests in a repository. state: 'open', 'closed', or 'all'."""
    return _request(
        "GET",
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "per_page": per_page, "page": page},
    )


@mcp.tool()
def get_pull_request(owner: str, repo: str, pr_number: int) -> dict:
    """Get a single pull request by number."""
    return _request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")


@mcp.tool()
def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: str = "",
    draft: bool = False,
) -> dict:
    """Create a pull request. 'head' is the source branch, 'base' is the target branch.
    Requires a token with repo access.
    """
    payload = {"title": title, "head": head, "base": base, "body": body, "draft": draft}
    return _request("POST", f"/repos/{owner}/{repo}/pulls", json=payload)


@mcp.tool()
def merge_pull_request(
    owner: str, repo: str, pr_number: int, merge_method: str = "merge"
) -> dict:
    """Merge a pull request. merge_method: 'merge', 'squash', or 'rebase'.
    Requires a token with repo access.
    """
    return _request(
        "PUT",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        json={"merge_method": merge_method},
    )


@mcp.tool()
def list_pull_request_files(owner: str, repo: str, pr_number: int, per_page: int = 30) -> list:
    """List the files changed in a pull request."""
    return _request(
        "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/files", params={"per_page": per_page}
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@mcp.tool()
def search_code(query: str, per_page: int = 10) -> dict:
    """Search code across GitHub. Example query: 'addClass in:file language:js repo:jquery/jquery'."""
    return _request("GET", "/search/code", params={"q": query, "per_page": per_page})


@mcp.tool()
def search_issues(query: str, per_page: int = 10) -> dict:
    """Search issues and pull requests across GitHub using GitHub search syntax."""
    return _request("GET", "/search/issues", params={"q": query, "per_page": per_page})


@mcp.tool()
def search_users(query: str, per_page: int = 10) -> dict:
    """Search GitHub users."""
    return _request("GET", "/search/users", params={"q": query, "per_page": per_page})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not TOKEN:
        print(
            "Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set. "
            "Read-only public endpoints will work but with lower rate limits; "
            "write operations (create_issue, create_pull_request, etc.) will fail.",
            file=sys.stderr,
        )
    mcp.run(transport="stdio")