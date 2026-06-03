from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from git import Repo, InvalidGitRepositoryError, NoSuchPathError


@dataclass
class CommitRecord:
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    files_changed: list[str]
    insertions: int
    deletions: int
    total_changes: int


def validate_repo(repo_path: str | Path) -> Repo:
    """Validate and return a GitPython Repo object."""
    path = Path(repo_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {path}")

    try:
        return Repo(path, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        raise ValueError(f"Not a valid Git repository: {path}")


def read_commits(repo_path: str | Path, max_commits: int = 120) -> list[dict[str, Any]]:
    """Read recent commits and return structured commit dictionaries."""
    repo = validate_repo(repo_path)
    commits: list[CommitRecord] = []

    for commit in repo.iter_commits(max_count=max_commits):
        stats = commit.stats.total
        files_changed = list(commit.stats.files.keys())

        commits.append(
            CommitRecord(
                hash=commit.hexsha,
                short_hash=commit.hexsha[:7],
                author=commit.author.name or "Unknown",
                email=commit.author.email or "",
                date=commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                message=(commit.message or "").strip().replace("\n", " "),
                files_changed=files_changed,
                insertions=int(stats.get("insertions", 0)),
                deletions=int(stats.get("deletions", 0)),
                total_changes=int(stats.get("lines", 0)),
            )
        )

    commits.reverse()  # oldest -> newest for storytelling
    return [asdict(c) for c in commits]
