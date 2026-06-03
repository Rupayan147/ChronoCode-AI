from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any


def _month_key(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
    except ValueError:
        return date_str[:7]


def analyze_commits(commits: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate useful statistics from commit records."""
    if not commits:
        return {
            "total_commits": 0,
            "total_authors": 0,
            "authors": {},
            "top_files": [],
            "activity_by_month": {},
            "first_commit_date": None,
            "latest_commit_date": None,
            "biggest_commits": [],
            "total_insertions": 0,
            "total_deletions": 0,
        }

    author_counter = Counter(c["author"] for c in commits)
    file_counter: Counter[str] = Counter()
    monthly_counter: Counter[str] = Counter()
    total_insertions = 0
    total_deletions = 0

    for c in commits:
        total_insertions += int(c.get("insertions", 0))
        total_deletions += int(c.get("deletions", 0))
        monthly_counter[_month_key(c["date"])] += 1
        for file in c.get("files_changed", []):
            file_counter[file] += 1

    biggest_commits = sorted(
        commits,
        key=lambda c: (len(c.get("files_changed", [])), int(c.get("total_changes", 0))),
        reverse=True,
    )[:5]

    return {
        "total_commits": len(commits),
        "total_authors": len(author_counter),
        "authors": dict(author_counter.most_common()),
        "top_files": file_counter.most_common(10),
        "activity_by_month": dict(sorted(monthly_counter.items())),
        "first_commit_date": commits[0]["date"],
        "latest_commit_date": commits[-1]["date"],
        "biggest_commits": biggest_commits,
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
    }


def build_commit_digest(commits: list[dict[str, Any]], limit: int = 40) -> str:
    """Compact commit history digest for LLM prompt/report."""
    selected = commits[-limit:]
    lines = []
    for c in selected:
        files = ", ".join(c.get("files_changed", [])[:6])
        if len(c.get("files_changed", [])) > 6:
            files += ", ..."
        lines.append(
            f"- {c['date']} | {c['short_hash']} | {c['author']} | {c['message']} "
            f"| +{c['insertions']}/-{c['deletions']} | files: {files}"
        )
    return "\n".join(lines)
