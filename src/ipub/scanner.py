"""Scan notes directory and identify publishable candidates."""

from pathlib import Path
from datetime import datetime

import click
import frontmatter
from rich.console import Console
from rich.table import Table

from ipub.config import load_config
from ipub.storage import Storage
from ipub.llm import call_llm

console = Console()


def scan_notes(directory: Path, storage: Storage, min_score: float) -> list[dict]:
    """Scan a directory for notes that are worth publishing."""
    config = load_config()
    extensions = config["scan"]["extensions"]
    ignore_dirs = config["scan"]["ignore"]
    min_words = config["scan"]["min_words"]

    # Collect all note files
    note_files = []
    for ext in extensions:
        for f in directory.rglob(f"*{ext}"):
            if any(ignore in f.parts for ignore in ignore_dirs):
                continue
            note_files.append(f)

    if not note_files:
        click.echo(f"No note files found in {directory}")
        return []

    click.echo(f"Found {len(note_files)} note file(s). Evaluating...")

    candidates = []
    for f in note_files:
        content = f.read_text(encoding="utf-8", errors="ignore")

        # Basic filter: skip very short notes
        word_count = len(content.split())
        if word_count < min_words:
            continue

        # Extract frontmatter if exists
        try:
            post = frontmatter.loads(content)
            meta = dict(post.metadata)
            body = post.content
        except Exception:
            meta = {}
            body = content

        # Use LLM to evaluate publishability
        evaluation = evaluate_note(f, body, meta)

        if evaluation["score"] >= min_score:
            candidate = {
                "source_path": str(f.resolve()),
                "title": evaluation.get("title", f.stem),
                "score": evaluation["score"],
                "reason": evaluation["reason"],
                "content_type": evaluation.get("content_type", "article"),
                "risk_flags": evaluation.get("risk_flags", []),
                "word_count": word_count,
                "scanned_at": datetime.now().isoformat(),
                "status": "scanned",
            }
            candidates.append(candidate)
            storage.add_candidate(candidate)

    # Display results
    if candidates:
        display_candidates(candidates)

    return candidates


def evaluate_note(file_path: Path, content: str, meta: dict) -> dict:
    """Use LLM to evaluate if a note is worth publishing."""
    # Truncate very long content to save tokens
    max_chars = 8000
    truncated = content[:max_chars] + ("..." if len(content) > max_chars else "")

    prompt = f"""Evaluate this technical note for publishability.

File: {file_path.name}
Metadata: {meta}

Content:
{truncated}

Respond in YAML format only:
```yaml
title: "suggested title for publishing"
score: 0.0-1.0  # how publishable is this note
reason: "one line explanation"
content_type: "tutorial|writeup|analysis|notes|guide"
risk_flags:
  - "list any concerns (sensitive paths, internal info, incomplete content)"
```

Scoring guide:
- 0.8+: Complete, well-structured, directly publishable
- 0.6-0.8: Good content but needs some editing
- 0.4-0.6: Has value but needs significant work
- <0.4: Not suitable for publishing (fragment, too short, private)
"""

    response = call_llm(prompt)
    return _parse_evaluation(response)


def _parse_evaluation(response: str) -> dict:
    """Parse LLM evaluation response."""
    import yaml

    # Extract YAML from response
    yaml_str = response
    if "```yaml" in response:
        yaml_str = response.split("```yaml")[1].split("```")[0]
    elif "```" in response:
        yaml_str = response.split("```")[1].split("```")[0]

    try:
        result = yaml.safe_load(yaml_str)
        if isinstance(result, dict):
            result.setdefault("score", 0.5)
            result.setdefault("reason", "")
            result.setdefault("title", "Untitled")
            result.setdefault("content_type", "article")
            result.setdefault("risk_flags", [])
            return result
    except Exception:
        pass

    return {
        "score": 0.5,
        "reason": "Could not evaluate automatically",
        "title": "Untitled",
        "content_type": "article",
        "risk_flags": ["evaluation_failed"],
    }


def display_candidates(candidates: list[dict]):
    """Display candidates in a table."""
    table = Table(title="Publishable Candidates")
    table.add_column("Score", style="bold", width=6)
    table.add_column("Title", width=40)
    table.add_column("Type", width=10)
    table.add_column("Words", width=8, justify="right")
    table.add_column("Risks", width=20)

    for c in sorted(candidates, key=lambda x: x["score"], reverse=True):
        score = c["score"]
        if score >= 0.8:
            score_str = f"[green]{score:.1f}[/green]"
        elif score >= 0.6:
            score_str = f"[yellow]{score:.1f}[/yellow]"
        else:
            score_str = f"[red]{score:.1f}[/red]"

        risks = ", ".join(c.get("risk_flags", [])) or "-"
        table.add_row(
            score_str,
            c["title"],
            c["content_type"],
            str(c["word_count"]),
            risks,
        )

    console.print(table)
