"""ipub CLI entry point."""

import click
from pathlib import Path

from ipub.scanner import scan_notes
from ipub.drafter import create_draft
from ipub.reviewer import list_reviews, approve_draft, reject_draft
from ipub.storage import Storage
from ipub.config import load_config, init_config
from ipub.connectors.feishu import pull_feishu_docs, pull_feishu_wiki


@click.group()
@click.pass_context
def main(ctx):
    """ipub - Turn your technical notes into publishable content."""
    ctx.ensure_object(dict)
    ctx.obj["storage"] = Storage()


@main.command()
def init():
    """Initialize ipub in the current directory."""
    config_path = init_config()
    storage = Storage()
    storage.init()
    click.echo(f"Initialized ipub.")
    click.echo(f"  Config: {config_path}")
    click.echo(f"  Data:   .ipub/")
    click.echo()
    click.echo("Next: ipub scan <notes-directory>")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--min-score", default=0.5, help="Minimum score to be a candidate (0.0-1.0)")
@click.pass_context
def scan(ctx, directory, min_score):
    """Scan a directory for publishable notes."""
    storage = ctx.obj["storage"]
    storage.ensure_initialized()
    candidates = scan_notes(Path(directory), storage, min_score)
    if not candidates:
        click.echo("No publishable candidates found.")
    else:
        click.echo(f"Found {len(candidates)} candidate(s).")


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--platforms", "-p", multiple=True, default=["blog"],
              help="Target platforms (blog, csdn, zhihu, feishu)")
@click.pass_context
def draft(ctx, file_path, platforms):
    """Generate a publishable draft from a note."""
    storage = ctx.obj["storage"]
    storage.ensure_initialized()
    draft_id = create_draft(Path(file_path), list(platforms), storage)
    click.echo(f"Draft created: {draft_id}")
    click.echo(f"  Review: ipub review {draft_id}")


@main.command()
@click.argument("draft_id", required=False)
@click.pass_context
def review(ctx, draft_id):
    """Review pending drafts. Show all or a specific draft."""
    storage = ctx.obj["storage"]
    storage.ensure_initialized()
    list_reviews(storage, draft_id)


@main.command()
@click.argument("draft_id")
@click.option("--platform", "-p", multiple=True, help="Platforms to export for")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.pass_context
def approve(ctx, draft_id, platform, output):
    """Approve a draft and export for publishing."""
    storage = ctx.obj["storage"]
    storage.ensure_initialized()
    approve_draft(storage, draft_id, list(platform) if platform else None, output)


@main.command()
@click.argument("draft_id")
@click.option("--reason", "-r", default="", help="Reason for rejection")
@click.pass_context
def reject(ctx, draft_id, reason):
    """Reject a draft."""
    storage = ctx.obj["storage"]
    storage.ensure_initialized()
    reject_draft(storage, draft_id, reason)


@main.group()
def pull():
    """Pull notes from external platforms."""
    pass


@pull.command(name="feishu")
@click.option("--folder", "-f", default=None, help="Feishu folder token")
@click.option("--output", "-o", default="./feishu-notes", help="Output directory")
@click.option("--app-id", envvar="FEISHU_APP_ID", help="Feishu App ID")
@click.option("--app-secret", envvar="FEISHU_APP_SECRET", help="Feishu App Secret")
def pull_feishu(folder, output, app_id, app_secret):
    """Pull documents from Feishu drive."""
    pull_feishu_docs(
        output_dir=Path(output),
        folder_token=folder,
        app_id=app_id,
        app_secret=app_secret,
    )
    click.echo(f"\nNext: ipub scan {output}")


@pull.command(name="feishu-wiki")
@click.argument("space_id")
@click.option("--output", "-o", default="./feishu-wiki", help="Output directory")
@click.option("--app-id", envvar="FEISHU_APP_ID", help="Feishu App ID")
@click.option("--app-secret", envvar="FEISHU_APP_SECRET", help="Feishu App Secret")
def pull_feishu_wiki_cmd(space_id, output, app_id, app_secret):
    """Pull pages from a Feishu wiki space."""
    pull_feishu_wiki(
        output_dir=Path(output),
        space_id=space_id,
        app_id=app_id,
        app_secret=app_secret,
    )
    click.echo(f"\nNext: ipub scan {output}")


if __name__ == "__main__":
    main()
