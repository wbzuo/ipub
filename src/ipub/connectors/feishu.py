"""Feishu (Lark) connector - pull documents from Feishu and save as local markdown."""

import os
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import click


FEISHU_BASE = "https://open.feishu.cn/open-apis"


class FeishuClient:
    """Client for Feishu Open API."""

    def __init__(self, app_id: str | None = None, app_secret: str | None = None):
        # Priority: argument > env var > ipub.yaml
        from ipub.config import load_config
        config = load_config()
        feishu_config = config.get("feishu", {})

        self.app_id = app_id or os.environ.get("FEISHU_APP_ID", "") or feishu_config.get("app_id", "")
        self.app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET", "") or feishu_config.get("app_secret", "")
        if not self.app_id or not self.app_secret:
            raise RuntimeError(
                "Feishu credentials not set. Either:\n"
                "  1. export FEISHU_APP_ID=xxx && export FEISHU_APP_SECRET=xxx\n"
                "  2. Set feishu.app_id and feishu.app_secret in ipub.yaml"
            )
        self._token = None
        self._token_expires = 0

    @property
    def token(self) -> str:
        """Get tenant access token, refreshing if expired."""
        if self._token and time.time() < self._token_expires:
            return self._token

        resp = self._post(
            "/auth/v3/tenant_access_token/internal",
            {"app_id": self.app_id, "app_secret": self.app_secret},
            auth=False,
        )
        self._token = resp["tenant_access_token"]
        self._token_expires = time.time() + resp.get("expire", 7200) - 60
        return self._token

    def list_docs(self, folder_token: str | None = None) -> list[dict]:
        """List documents in a folder or root drive."""
        params = "?folder_token=" + folder_token if folder_token else ""
        resp = self._get(f"/drive/v1/files{params}")
        files = resp.get("data", {}).get("files", [])
        # Filter for documents only
        return [f for f in files if f.get("type") in ("docx", "doc")]

    def get_wiki_node_info(self, node_token: str) -> dict:
        """Get info about a wiki node, including space_id and obj_token."""
        resp = self._get(f"/wiki/v2/spaces/get_node?token={node_token}")
        return resp.get("data", {}).get("node", {})

    def list_wiki_nodes(self, space_id: str, parent_node_token: str | None = None) -> list[dict]:
        """List nodes in a wiki space."""
        params = ""
        if parent_node_token:
            params = f"?parent_node_token={parent_node_token}"
        resp = self._get(f"/wiki/v2/spaces/{space_id}/nodes{params}")
        return resp.get("data", {}).get("items", [])

    def get_document_content(self, document_id: str) -> dict:
        """Get document raw content as structured blocks."""
        resp = self._get(f"/docx/v1/documents/{document_id}/raw_content")
        return resp.get("data", {})

    def get_document_blocks(self, document_id: str) -> list[dict]:
        """Get document as a list of blocks."""
        resp = self._get(f"/docx/v1/documents/{document_id}/blocks")
        return resp.get("data", {}).get("items", [])

    def get_document_meta(self, document_id: str) -> dict:
        """Get document metadata (title, create time, etc.)."""
        resp = self._get(f"/docx/v1/documents/{document_id}")
        return resp.get("data", {}).get("document", {})

    def _get(self, path: str) -> dict:
        """Make authenticated GET request."""
        url = FEISHU_BASE + path
        req = Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"Feishu API error: {e.code} {body}") from e

    def _post(self, path: str, data: dict, auth: bool = True) -> dict:
        """Make POST request."""
        url = FEISHU_BASE + path
        body = json.dumps(data).encode("utf-8")
        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        if auth:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"Feishu API error: {e.code} {body}") from e


def blocks_to_markdown(blocks: list[dict]) -> str:
    """Convert Feishu document blocks to markdown."""
    lines = []
    for block in blocks:
        block_type = block.get("block_type")

        if block_type == 1:  # Page / title
            # Skip, handled by metadata
            pass

        elif block_type == 2:  # Text
            text = _extract_text(block)
            if text:
                lines.append(text)
                lines.append("")

        elif block_type == 3:  # Heading 1
            text = _extract_text(block)
            if text:
                lines.append(f"# {text}")
                lines.append("")

        elif block_type == 4:  # Heading 2
            text = _extract_text(block)
            if text:
                lines.append(f"## {text}")
                lines.append("")

        elif block_type == 5:  # Heading 3
            text = _extract_text(block)
            if text:
                lines.append(f"### {text}")
                lines.append("")

        elif block_type == 6:  # Heading 4
            text = _extract_text(block)
            if text:
                lines.append(f"#### {text}")
                lines.append("")

        elif block_type == 7:  # Heading 5
            text = _extract_text(block)
            if text:
                lines.append(f"##### {text}")
                lines.append("")

        elif block_type == 8:  # Heading 6
            text = _extract_text(block)
            if text:
                lines.append(f"###### {text}")
                lines.append("")

        elif block_type == 9:  # Heading 7-9
            text = _extract_text(block)
            if text:
                lines.append(f"###### {text}")
                lines.append("")

        elif block_type == 10:  # Bullet list
            text = _extract_text(block)
            if text:
                lines.append(f"- {text}")

        elif block_type == 11:  # Ordered list
            text = _extract_text(block)
            if text:
                lines.append(f"1. {text}")

        elif block_type == 12:  # Code block
            code = _extract_text(block)
            lang = block.get("code", {}).get("style", {}).get("language", "")
            lines.append(f"```{lang}")
            lines.append(code)
            lines.append("```")
            lines.append("")

        elif block_type == 13:  # Quote
            text = _extract_text(block)
            if text:
                lines.append(f"> {text}")
                lines.append("")

        elif block_type == 14:  # Todo
            text = _extract_text(block)
            done = block.get("todo", {}).get("style", {}).get("done", False)
            checkbox = "[x]" if done else "[ ]"
            if text:
                lines.append(f"- {checkbox} {text}")

        elif block_type == 15:  # Divider
            lines.append("---")
            lines.append("")

        elif block_type == 17:  # Table
            # Simplified table handling
            lines.append("[表格内容]")
            lines.append("")

        elif block_type == 27:  # Image
            image_key = block.get("image", {}).get("image_key", "")
            lines.append(f"![image]({image_key})")
            lines.append("")

        else:
            # Unknown block type, try to extract text
            text = _extract_text(block)
            if text:
                lines.append(text)
                lines.append("")

    return "\n".join(lines)


def _extract_text(block: dict) -> str:
    """Extract plain text from a block's text elements."""
    # Try different block type keys
    for key in ("text", "heading1", "heading2", "heading3", "heading4",
                "heading5", "heading6", "heading7", "heading8", "heading9",
                "bullet", "ordered", "code", "quote", "todo"):
        content = block.get(key, {})
        elements = content.get("elements", [])
        if elements:
            parts = []
            for elem in elements:
                text_run = elem.get("text_run", {})
                text = text_run.get("content", "")
                if text:
                    style = text_run.get("text_element_style", {})
                    if style.get("bold"):
                        text = f"**{text}**"
                    if style.get("italic"):
                        text = f"*{text}*"
                    if style.get("inline_code"):
                        text = f"`{text}`"
                    link = style.get("link", {}).get("url", "")
                    if link:
                        text = f"[{text}]({link})"
                parts.append(text)
            return "".join(parts)
    return ""


def pull_feishu_docs(
    output_dir: Path,
    folder_token: str | None = None,
    app_id: str | None = None,
    app_secret: str | None = None,
) -> list[Path]:
    """Pull documents from Feishu and save as local markdown files.

    Args:
        output_dir: Directory to save markdown files
        folder_token: Feishu folder token (None for root)
        app_id: Feishu App ID (or set FEISHU_APP_ID env)
        app_secret: Feishu App Secret (or set FEISHU_APP_SECRET env)

    Returns:
        List of saved file paths
    """
    client = FeishuClient(app_id, app_secret)
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo("Connecting to Feishu...")
    docs = client.list_docs(folder_token)

    if not docs:
        click.echo("No documents found.")
        return []

    click.echo(f"Found {len(docs)} document(s). Pulling...")

    saved = []
    for doc in docs:
        doc_token = doc.get("token", "")
        doc_name = doc.get("name", "untitled")
        click.echo(f"  Pulling: {doc_name}")

        try:
            # Get document blocks
            blocks = client.get_document_blocks(doc_token)

            # Convert to markdown
            md_content = blocks_to_markdown(blocks)

            # Add frontmatter
            meta = client.get_document_meta(doc_token)
            frontmatter = (
                f"---\n"
                f"title: \"{doc_name}\"\n"
                f"source: feishu\n"
                f"feishu_token: {doc_token}\n"
                f"created: {meta.get('created_time', '')}\n"
                f"updated: {meta.get('modified_time', '')}\n"
                f"---\n\n"
            )

            # Save
            safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in doc_name)
            file_path = output_dir / f"{safe_name}.md"
            file_path.write_text(frontmatter + md_content, encoding="utf-8")
            saved.append(file_path)
            click.echo(f"    Saved: {file_path}")

        except Exception as e:
            click.echo(f"    Error: {e}")

    click.echo(f"\nPulled {len(saved)} document(s) to {output_dir}")
    return saved


def pull_feishu_wiki(
    output_dir: Path,
    token: str,
    app_id: str | None = None,
    app_secret: str | None = None,
) -> list[Path]:
    """Pull wiki pages from Feishu. Accepts space_id, node_token, or wiki URL.

    Args:
        output_dir: Directory to save markdown files
        token: Feishu wiki space_id, node_token, or full URL
        app_id: Feishu App ID
        app_secret: Feishu App Secret

    Returns:
        List of saved file paths
    """
    client = FeishuClient(app_id, app_secret)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse URL if given
    if "feishu.cn" in token:
        import re
        match = re.search(r"/wiki/([A-Za-z0-9]+)", token)
        if match:
            token = match.group(1)
            click.echo(f"Extracted token from URL: {token}")
        else:
            raise click.ClickException(f"Cannot parse wiki token from URL: {token}")

    # Try as node_token first — get space_id from it
    click.echo(f"Looking up token: {token}")
    try:
        node_info = client.get_wiki_node_info(token)
        space_id = node_info.get("space_id", "")
        parent_node = node_info.get("node_token", "")
        node_title = node_info.get("title", "")
        if space_id:
            click.echo(f"Found wiki space: {space_id}, page: {node_title}")
            # Pull this node as a document + its children
            nodes = client.list_wiki_nodes(space_id, parent_node_token=parent_node)
            # Also include the node itself
            if node_info.get("obj_type") == "docx":
                nodes = [node_info] + nodes
        else:
            raise RuntimeError("No space_id found")
    except Exception:
        # Maybe it's a space_id directly
        click.echo(f"Trying as space_id: {token}")
        space_id = token
        nodes = client.list_wiki_nodes(space_id)

    if not nodes:
        click.echo("No wiki pages found.")
        return []

    # Recursively collect all nodes (including children of children)
    all_nodes = []
    _collect_nodes_recursive(client, space_id, nodes, all_nodes, depth=0)

    click.echo(f"Found {len(all_nodes)} page(s) total. Pulling...")

    saved = []
    for node, depth in all_nodes:
        node_token = node.get("node_token", "")
        obj_token = node.get("obj_token", "")
        title = node.get("title", "untitled")
        node_type = node.get("obj_type", "")

        if node_type != "docx":
            click.echo(f"{'  ' * (depth + 1)}Skipping non-doc: {title} ({node_type})")
            continue

        indent = "  " * (depth + 1)
        click.echo(f"{indent}Pulling: {title}")
        try:
            blocks = client.get_document_blocks(obj_token)
            md_content = blocks_to_markdown(blocks)

            # Skip empty documents
            if not md_content.strip():
                click.echo(f"{indent}  (empty, skipped)")
                continue

            frontmatter = (
                f"---\n"
                f"title: \"{title}\"\n"
                f"source: feishu_wiki\n"
                f"space_id: {space_id}\n"
                f"node_token: {node_token}\n"
                f"---\n\n"
            )

            safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title)
            file_path = output_dir / f"{safe_name}.md"
            file_path.write_text(frontmatter + md_content, encoding="utf-8")
            saved.append(file_path)
            click.echo(f"{indent}  Saved: {file_path}")

        except Exception as e:
            click.echo(f"{indent}  Error: {e}")

    click.echo(f"\nPulled {len(saved)} page(s) to {output_dir}")
    return saved


def _collect_nodes_recursive(
    client: FeishuClient,
    space_id: str,
    nodes: list[dict],
    result: list[tuple[dict, int]],
    depth: int,
    max_depth: int = 10,
):
    """Recursively collect all wiki nodes including children."""
    if depth > max_depth:
        return

    for node in nodes:
        result.append((node, depth))
        node_token = node.get("node_token", "")
        has_child = node.get("has_child", False)

        if has_child and node_token:
            try:
                children = client.list_wiki_nodes(space_id, parent_node_token=node_token)
                if children:
                    _collect_nodes_recursive(client, space_id, children, result, depth + 1, max_depth)
            except Exception as e:
                click.echo(f"{'  ' * (depth + 2)}Error listing children of {node.get('title', '')}: {e}")
