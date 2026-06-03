from __future__ import annotations

import textwrap
from typing import Any

from .analyzer import build_commit_digest
from .config import GEMINI_API_KEY


def _fallback_story(analysis: dict[str, Any], commits: list[dict[str, Any]]) -> str:
    if not commits:
        return "No commits were found, so ChronoCode could not build a project narrative."

    top_files = analysis.get("top_files", [])[:5]
    top_file_text = ", ".join([f"{name} ({count})" for name, count in top_files]) or "No dominant files detected"
    authors = ", ".join(analysis.get("authors", {}).keys()) or "Unknown"

    first = analysis.get("first_commit_date")
    latest = analysis.get("latest_commit_date")
    recent_messages = [c["message"] for c in commits[-6:]]

    return textwrap.dedent(
        f"""
        ## Project Evolution Story

        This repository evolved across **{analysis.get('total_commits', 0)} commits** between **{first}** and **{latest}**.
        The work was mainly contributed by **{authors}**.

        ### Chapter 1 — Foundation
        The early commits establish the base structure of the project. The repository begins with core files, setup work, and the first usable version of the codebase.

        ### Chapter 2 — Expansion
        As the project grows, several files become central to development. The most frequently changed areas are: **{top_file_text}**. These files likely represent the main product surface or core logic.

        ### Chapter 3 — Refinement
        The latest commits suggest active polishing and iteration. Recent work includes:
        {chr(10).join([f'- {m}' for m in recent_messages])}

        ### Final Summary
        ChronoCode detects a project moving from initial setup toward a more complete, refined implementation. The commit pattern shows practical development: building the foundation, expanding features, and improving the result.
        """
    ).strip()


def generate_story(analysis: dict[str, Any], commits: list[dict[str, Any]]) -> str:
    """Generate a narrative using Gemini if configured, otherwise fallback locally."""
    if not GEMINI_API_KEY:
        return _fallback_story(analysis, commits)

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        digest = build_commit_digest(commits)
        prompt = f"""
You are a technical storyteller and senior software engineer.

Based on this Git repository analysis and commit history, write a clear project evolution story.
Do not exaggerate. Use specific patterns from the commit history.

Required structure:
1. Short project overview
2. 3-5 timeline chapters
3. Major features or milestones
4. Refactors / fixes / polish patterns
5. Final evolution summary

Analysis:
{analysis}

Commit digest:
{digest}
"""
        response = model.generate_content(prompt)
        return (response.text or "").strip() or _fallback_story(analysis, commits)
    except Exception as exc:
        return _fallback_story(analysis, commits) + f"\n\n> AI note: Gemini generation failed, fallback story used. Error: {exc}"
