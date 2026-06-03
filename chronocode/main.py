from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .repo_loader import load_repo
from .git_parser import read_commits
from .analyzer import analyze_commits
from .ai_writer import generate_story
from .report_generator import generate_markdown_report

app = typer.Typer(help="ChronoCode AI: turn Git history into readable project narratives.")
console = Console()


def _load(repo_path: str, max_commits: int):
    commits = read_commits(repo_path, max_commits=max_commits)
    if not commits:
        raise typer.BadParameter("No commits found in this repository.")
    analysis = analyze_commits(commits)
    return commits, analysis


@app.command()
def analyze(
    repo_input: str = typer.Argument(..., help="Path to a local Git repository or a public GitHub URL."),
    max_commits: int = typer.Option(120, help="Maximum commits to analyze."),
):
    """Analyze repository history and print key metrics."""
    try:
        repo_path = load_repo(repo_input)
        commits, analysis = _load(repo_path, max_commits)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(Panel.fit("[bold cyan]ChronoCode AI Repository Analysis[/bold cyan]"))

    summary = Table(title="Summary", show_header=True, header_style="bold magenta")
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")
    summary.add_row("Total commits", str(analysis["total_commits"]))
    summary.add_row("Total authors", str(analysis["total_authors"]))
    summary.add_row("Insertions", str(analysis["total_insertions"]))
    summary.add_row("Deletions", str(analysis["total_deletions"]))
    summary.add_row("First commit", str(analysis["first_commit_date"]))
    summary.add_row("Latest commit", str(analysis["latest_commit_date"]))
    console.print(summary)

    authors = Table(title="Author Activity", show_header=True, header_style="bold green")
    authors.add_column("Author")
    authors.add_column("Commits", justify="right")
    for author, count in analysis["authors"].items():
        authors.add_row(author, str(count))
    console.print(authors)

    files = Table(title="Most Changed Files", show_header=True, header_style="bold yellow")
    files.add_column("File")
    files.add_column("Changes", justify="right")
    for file, count in analysis["top_files"][:10]:
        files.add_row(file, str(count))
    console.print(files)


@app.command()
def story(
    repo_input: str = typer.Argument(..., help="Path to a local Git repository or a public GitHub URL."),
    max_commits: int = typer.Option(120, help="Maximum commits to analyze."),
):
    """Generate a readable project evolution story."""
    try:
        repo_path = load_repo(repo_input)
        commits, analysis = _load(repo_path, max_commits)
        narrative = generate_story(analysis, commits)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(Panel.fit("[bold cyan]Codebase Evolution Story[/bold cyan]"))
    console.print(Markdown(narrative))


@app.command()
def report(
    repo_input: str = typer.Argument(..., help="Path to a local Git repository or a public GitHub URL."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Markdown output path."),
    max_commits: int = typer.Option(120, help="Maximum commits to analyze."),
):
    """Generate a Markdown code archaeology report."""
    try:
        repo_path = load_repo(repo_input)
        commits, analysis = _load(repo_path, max_commits)
        narrative = generate_story(analysis, commits)
        report_path = generate_markdown_report(repo_path, analysis, commits, narrative, output)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Report generated:[/bold green] {report_path.resolve()}")


if __name__ == "__main__":
    app()
