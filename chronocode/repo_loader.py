from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console


console = Console()
CACHE_DIR_NAME = ".chronocode_cache"


def load_repo(repo_input: str) -> str:
    """Resolve a local repository path or clone a public GitHub repository."""
    repo_input = repo_input.strip()
    if not repo_input:
        raise ValueError("Repository input cannot be empty.")

    if repo_input.startswith("https://github.com/"):
        return _load_github_repo(repo_input)

    with console.status("[cyan]Using local repository...[/cyan]"):
        pass
    return str(Path(repo_input).expanduser().resolve())


def _load_github_repo(repo_url: str) -> str:
    repo_name = _extract_repo_name(repo_url)
    if not repo_name:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    cache_dir = Path.cwd() / CACHE_DIR_NAME
    cache_dir.mkdir(exist_ok=True)

    repo_dir = cache_dir / repo_name
    if repo_dir.exists():
        if not (repo_dir / ".git").exists():
            raise ValueError(f"Cache path exists but is not a Git repository: {repo_dir}")

        with console.status("[cyan]Repository already exists, pulling latest changes...[/cyan]"):
            _run_git(["-C", str(repo_dir), "pull"])
        return str(repo_dir.resolve())

    with console.status("[cyan]Cloning repository...[/cyan]"):
        _run_git(["clone", repo_url, str(repo_dir)])
    return str(repo_dir.resolve())


def _extract_repo_name(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return ""

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        return ""

    owner, repo_name = parts
    if not owner or not repo_name:
        return ""

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    return repo_name


def _run_git(args: list[str]) -> None:
    if shutil.which("git") is None:
        raise FileNotFoundError("Git is not installed or is not available on PATH.")

    completed = subprocess.run(["git", *args], capture_output=True, text=True)
    if completed.returncode == 0:
        return

    stderr = (completed.stderr or "").strip()
    stdout = (completed.stdout or "").strip()
    message = stderr or stdout or "Git command failed."
    lowered = message.lower()

    if "repository not found" in lowered or "remote: repository not found" in lowered or "could not read from remote repository" in lowered:
        raise FileNotFoundError(f"Repo not found: {message}")

    raise RuntimeError(message)