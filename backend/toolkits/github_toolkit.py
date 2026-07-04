"""
Project TITAN — GitHub MCP Toolkit
Wraps GitHub repository creation and pushing logic into a CAMEL Toolkit
that can be exposed as an MCP Server.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

import git
from github import Github, GithubException
from loguru import logger

from camel.toolkits.base import BaseToolkit
from camel.toolkits import FunctionTool
from backend.config import GITHUB_TOKEN, GITHUB_USERNAME


class TITANGithubToolkit(BaseToolkit):
    """
    Toolkit for creating GitHub repositories and pushing code.
    Can be run as an MCP Server.
    """

    def get_tools(self) -> List[FunctionTool]:
        """Return a list of FunctionTools for this toolkit."""
        return [
            FunctionTool(self.create_github_repo),
            FunctionTool(self.git_init_and_commit),
            FunctionTool(self.git_push_code),
        ]

    def create_github_repo(self, repo_name: str, description: str = "", private: bool = False) -> str:
        """
        Creates a new GitHub repository for the authenticated user.
        
        Args:
            repo_name (str): Name of the new repository
            description (str): Description of the repository
            private (bool): Whether the repo should be private

        Returns:
            str: The full URL of the created or existing repository.
        """
        if not GITHUB_TOKEN:
            return "Error: GITHUB_TOKEN not configured in environment."

        gh = Github(GITHUB_TOKEN)
        try:
            user = gh.get_user()
            # Check if exists
            try:
                existing = user.get_repo(repo_name)
                logger.warning(f"Repo already exists: {existing.html_url}")
                return existing.html_url
            except GithubException:
                pass

            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=False,
            )
            logger.success(f"✅ GitHub repo created via MCP: {repo.html_url}")
            return repo.html_url
        except Exception as e:
            logger.error(f"Failed to create repo: {e}")
            return f"Error: {str(e)}"

    def git_init_and_commit(self, project_root: str, commit_message: str = "Initial commit") -> str:
        """
        Initializes a local git repository in the given directory, stages all files, and creates an initial commit.
        
        Args:
            project_root (str): Absolute path to the project directory
            commit_message (str): Message for the initial commit

        Returns:
            str: Success or error message
        """
        root = Path(project_root)
        if not root.exists():
            return f"Error: Path {project_root} does not exist."

        try:
            # Init
            if (root / ".git").exists():
                repo = git.Repo(root)
            else:
                repo = git.Repo.init(root)
            
            # Add all
            repo.git.add(A=True)
            
            # Commit
            if not repo.index.diff("HEAD") and not repo.untracked_files:
                try:
                    repo.head.commit
                    return "Success: Nothing to commit (already committed)"
                except Exception:
                    pass

            repo.index.commit(commit_message)
            return "Success: Git repo initialized and initial commit created."
        except Exception as e:
            return f"Error: {str(e)}"

    def git_push_code(self, project_root: str, repo_name: str, branches: List[str] = None) -> str:
        """
        Sets the remote URL to the GitHub repository and pushes the specified branches.
        
        Args:
            project_root (str): Absolute path to the project directory
            repo_name (str): Name of the repository on GitHub
            branches (list): List of branch names to push (defaults to ['main'])

        Returns:
            str: Success or error message
        """
        if not GITHUB_TOKEN or not GITHUB_USERNAME:
            return "Error: GitHub credentials missing."

        root = Path(project_root)
        if not (root / ".git").exists():
            return "Error: Not a git repository."

        if branches is None:
            branches = ["main"]

        remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"

        try:
            repo = git.Repo(root)
            # Set remote
            try:
                remote = repo.remote("origin")
                remote.set_url(remote_url)
            except ValueError:
                repo.create_remote("origin", remote_url)

            # Ensure default branch is main or master
            current = repo.active_branch.name
            if current not in ["main", "master"]:
                try:
                    repo.git.branch("-M", "main")
                    current = "main"
                except Exception:
                    pass

            # Push logic via subprocess since GitPython can be finicky with auth
            pushed = []
            for branch in branches:
                if branch != current:
                    try:
                        repo.git.checkout("-b", branch)
                    except Exception:
                        pass
                
                cmd = f"git push origin {branch} --set-upstream"
                result = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
                if result.returncode == 0:
                    pushed.append(branch)
                else:
                    return f"Error pushing branch {branch}: {result.stderr}"

            return f"Success: Pushed branches {', '.join(pushed)} to {repo_name}"
        except Exception as e:
            return f"Error: {str(e)}"
