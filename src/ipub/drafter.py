"""Draft generation - compile notes into publishable content."""

from pathlib import Path
from datetime import datetime

import click
import frontmatter
import yaml

from ipub.config import load_config
from ipub.storage import Storage
from ipub.llm import call_llm


def create_draft(file_path: Path, platforms: list[str], storage: Storage) -> str:
    """Create a publishable draft from a source note."""
    config = load_config()

    # Read source
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    try:
        post = frontmatter.loads(content)
        meta = dict(post.metadata)
        body = post.content
    except Exception:
        meta = {}
        body = content

    # Generate draft via LLM
    click.echo(f"Generating draft from: {file_path.name}")
    draft_result = compile_note(body, meta, platforms, config)

    # Save draft
    draft_id = storage.next_draft_id()
    slug = _slugify(draft_result.get("title", file_path.stem))
    draft_dir = storage.create_draft_dir(draft_id, slug)

    # Save original
    (draft_dir / "original.md").write_text(content, encoding="utf-8")

    # Save main draft
    (draft_dir / "draft.md").write_text(draft_result["draft_long"], encoding="utf-8")

    # Save platform variants
    for platform, variant_content in draft_result.get("platform_variants", {}).items():
        (draft_dir / "platform" / f"{platform}.md").write_text(
            variant_content, encoding="utf-8"
        )

    # Save metadata
    draft_meta = {
        "id": draft_id,
        "title": draft_result.get("title", file_path.stem),
        "summary": draft_result.get("summary", ""),
        "title_candidates": draft_result.get("title_candidates", []),
        "source_path": str(file_path.resolve()),
        "platforms": platforms,
        "status": "pending_review",
        "created_at": datetime.now().isoformat(),
        "risk_flags": draft_result.get("risk_flags", []),
    }
    with open(draft_dir / "meta.yaml", "w") as f:
        yaml.dump(draft_meta, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    click.echo(f"  Title: {draft_meta['title']}")
    click.echo(f"  Summary: {draft_meta['summary']}")
    if draft_meta["title_candidates"]:
        click.echo(f"  Alt titles: {', '.join(draft_meta['title_candidates'][:3])}")
    if draft_meta["risk_flags"]:
        click.echo(f"  Risks: {', '.join(draft_meta['risk_flags'])}")

    return draft_id


def compile_note(body: str, meta: dict, platforms: list[str], config: dict) -> dict:
    """Use LLM to compile a note into publishable content."""
    style = config.get("style", {})
    avoid = style.get("avoid_phrases", [])
    tone = style.get("tone", "technical")
    language = style.get("language", "zh")

    platform_list = ", ".join(platforms)

    prompt = f"""You are a technical content editor. Convert this raw technical note into publishable content.

STYLE REQUIREMENTS:
- Tone: {tone}
- Language: {language}
- AVOID these phrases: {avoid}
- Keep the author's voice - polish, don't rewrite
- Preserve all code blocks, commands, and technical details
- Fix formatting issues but keep the structure

TARGET PLATFORMS: {platform_list}

ORIGINAL NOTE METADATA: {meta}

ORIGINAL NOTE:
{body}

Respond in YAML format:
```yaml
title: "best title for this content"
title_candidates:
  - "alternative title 1"
  - "alternative title 2"
  - "alternative title 3"
summary: "2-3 sentence summary"
draft_long: |
  Full publishable article in markdown format.
  Keep all code blocks and technical content.
  Improve structure, flow, and readability.
platform_variants:
  blog: |
    Blog-optimized version (markdown with frontmatter).
  csdn: |
    CSDN-optimized version (may need different formatting).
  zhihu: |
    Zhihu-optimized version (shorter, more conversational).
  feishu: |
    Feishu-optimized version.
risk_flags:
  - "list any issues found (local paths, sensitive info, etc.)"
```

Only include platform variants for: {platform_list}
"""

    response = call_llm(prompt)
    return _parse_draft(response)


def _parse_draft(response: str) -> dict:
    """Parse LLM draft response."""
    yaml_str = response
    if "```yaml" in response:
        yaml_str = response.split("```yaml")[1].split("```")[0]
    elif "```" in response:
        yaml_str = response.split("```")[1].split("```")[0]

    try:
        result = yaml.safe_load(yaml_str)
        if isinstance(result, dict):
            result.setdefault("title", "Untitled")
            result.setdefault("summary", "")
            result.setdefault("draft_long", "")
            result.setdefault("title_candidates", [])
            result.setdefault("platform_variants", {})
            result.setdefault("risk_flags", [])
            return result
    except Exception:
        pass

    # Fallback: use raw response as draft
    return {
        "title": "Untitled",
        "summary": "",
        "draft_long": response,
        "title_candidates": [],
        "platform_variants": {},
        "risk_flags": ["parse_failed"],
    }


def _slugify(text: str) -> str:
    """Create a simple slug from text."""
    import re
    slug = re.sub(r"[^\w\s-]", "", text)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:50].strip("-").lower() or "untitled"
