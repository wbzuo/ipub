"""Review and approve/reject drafts."""

from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

from ipub.storage import Storage

console = Console()


def list_reviews(storage: Storage, draft_id: str | None = None):
    """List all drafts or show a specific draft for review."""
    if draft_id:
        show_draft_detail(storage, draft_id)
        return

    drafts = storage.list_drafts()
    if not drafts:
        click.echo("No drafts found. Run: ipub draft <file>")
        return

    table = Table(title="Drafts")
    table.add_column("ID", style="bold", width=5)
    table.add_column("Title", width=40)
    table.add_column("Status", width=15)
    table.add_column("Platforms", width=20)
    table.add_column("Created", width=12)

    for d in drafts:
        status = d.get("status", "unknown")
        status_style = {
            "pending_review": "[yellow]pending[/yellow]",
            "approved": "[green]approved[/green]",
            "rejected": "[red]rejected[/red]",
            "published": "[blue]published[/blue]",
        }.get(status, status)

        platforms = ", ".join(d.get("platforms", []))
        created = d.get("created_at", "")[:10]

        table.add_row(
            d.get("id", "?"),
            d.get("title", "Untitled"),
            status_style,
            platforms,
            created,
        )

    console.print(table)


def show_draft_detail(storage: Storage, draft_id: str):
    """Show detailed view of a draft for review."""
    draft = storage.get_draft(draft_id)
    if draft is None:
        click.echo(f"Draft {draft_id} not found.")
        return

    draft_dir = Path(draft["_dir"])

    # Show metadata
    console.print(Panel(
        f"[bold]Title:[/bold] {draft.get('title', 'Untitled')}\n"
        f"[bold]Summary:[/bold] {draft.get('summary', '')}\n"
        f"[bold]Status:[/bold] {draft.get('status', 'unknown')}\n"
        f"[bold]Platforms:[/bold] {', '.join(draft.get('platforms', []))}\n"
        f"[bold]Source:[/bold] {draft.get('source_path', '')}\n"
        f"[bold]Risks:[/bold] {', '.join(draft.get('risk_flags', [])) or 'none'}",
        title=f"Draft {draft_id}",
    ))

    # Show title candidates
    candidates = draft.get("title_candidates", [])
    if candidates:
        console.print("\n[bold]Alternative titles:[/bold]")
        for i, t in enumerate(candidates, 1):
            console.print(f"  {i}. {t}")

    # Show draft content preview
    draft_file = draft_dir / "draft.md"
    if draft_file.exists():
        content = draft_file.read_text(encoding="utf-8")
        preview = content[:1000] + ("..." if len(content) > 1000 else "")
        console.print(Panel(preview, title="Draft Preview"))

    # Show available platform variants
    platform_dir = draft_dir / "platform"
    if platform_dir.exists():
        variants = [f.stem for f in platform_dir.iterdir() if f.suffix == ".md"]
        if variants:
            console.print(f"\n[bold]Platform variants:[/bold] {', '.join(variants)}")

    console.print(f"\n[dim]Approve: ipub approve {draft_id}")
    console.print(f"Reject:  ipub reject {draft_id}[/dim]")


def approve_draft(storage: Storage, draft_id: str, platforms: list[str] | None, output: str | None):
    """Approve a draft and export it."""
    draft = storage.get_draft(draft_id)
    if draft is None:
        click.echo(f"Draft {draft_id} not found.")
        return

    draft_dir = Path(draft["_dir"])

    # Determine platforms
    if not platforms:
        platforms = draft.get("platforms", ["blog"])

    # Determine output directory
    output_dir = Path(output) if output else storage.export_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export each platform variant
    exported = []
    for platform in platforms:
        platform_file = draft_dir / "platform" / f"{platform}.md"
        if platform_file.exists():
            content = platform_file.read_text(encoding="utf-8")
        else:
            # Fall back to main draft
            draft_file = draft_dir / "draft.md"
            content = draft_file.read_text(encoding="utf-8")

        # Write export file
        export_name = f"{draft_id}-{draft.get('title', 'untitled')}-{platform}.md"
        export_path = output_dir / export_name
        export_path.write_text(content, encoding="utf-8")
        exported.append((platform, export_path))
        click.echo(f"  Exported [{platform}]: {export_path}")

    # Update status
    storage.update_draft_meta(draft_id, {
        "status": "approved",
        "approved_at": datetime.now().isoformat(),
    })

    # Add to published record
    storage.add_published({
        "draft_id": draft_id,
        "title": draft.get("title", ""),
        "platforms": platforms,
        "exported_files": [str(p) for _, p in exported],
        "approved_at": datetime.now().isoformat(),
    })

    click.echo(f"\nDraft {draft_id} approved and exported.")


def reject_draft(storage: Storage, draft_id: str, reason: str):
    """Reject a draft."""
    draft = storage.get_draft(draft_id)
    if draft is None:
        click.echo(f"Draft {draft_id} not found.")
        return

    storage.update_draft_meta(draft_id, {
        "status": "rejected",
        "rejected_at": datetime.now().isoformat(),
        "reject_reason": reason,
    })

    click.echo(f"Draft {draft_id} rejected.")
    if reason:
        click.echo(f"  Reason: {reason}")
