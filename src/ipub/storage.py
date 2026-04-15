"""File-based storage for ipub. All data lives in .ipub/ directory."""

from pathlib import Path
from datetime import datetime
import yaml
import shutil

IPUB_DIR = ".ipub"


class Storage:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self.ipub_dir = self.root / IPUB_DIR
        self.candidates_file = self.ipub_dir / "candidates.yaml"
        self.drafts_dir = self.ipub_dir / "drafts"
        self.published_file = self.ipub_dir / "published.yaml"
        self.export_dir = self.ipub_dir / "export"

    def init(self):
        """Create .ipub/ directory structure."""
        self.ipub_dir.mkdir(exist_ok=True)
        self.drafts_dir.mkdir(exist_ok=True)
        self.export_dir.mkdir(exist_ok=True)
        if not self.candidates_file.exists():
            self._write_yaml(self.candidates_file, [])
        if not self.published_file.exists():
            self._write_yaml(self.published_file, [])

    def ensure_initialized(self):
        """Check that ipub has been initialized."""
        if not self.ipub_dir.exists():
            raise click.ClickException(
                "ipub not initialized. Run: ipub init"
            )

    def is_initialized(self) -> bool:
        return self.ipub_dir.exists()

    # --- Candidates ---

    def load_candidates(self) -> list[dict]:
        return self._read_yaml(self.candidates_file) or []

    def save_candidates(self, candidates: list[dict]):
        self._write_yaml(self.candidates_file, candidates)

    def add_candidate(self, candidate: dict):
        candidates = self.load_candidates()
        # Replace if same source path exists
        candidates = [c for c in candidates if c["source_path"] != candidate["source_path"]]
        candidates.append(candidate)
        self.save_candidates(candidates)

    def next_draft_id(self) -> str:
        """Generate next sequential draft ID."""
        existing = list(self.drafts_dir.iterdir()) if self.drafts_dir.exists() else []
        nums = []
        for d in existing:
            if d.is_dir() and d.name[:3].isdigit():
                nums.append(int(d.name[:3]))
        next_num = max(nums, default=0) + 1
        return f"{next_num:03d}"

    # --- Drafts ---

    def create_draft_dir(self, draft_id: str, slug: str) -> Path:
        """Create a directory for a draft."""
        dir_name = f"{draft_id}-{slug}"
        draft_dir = self.drafts_dir / dir_name
        draft_dir.mkdir(parents=True, exist_ok=True)
        (draft_dir / "platform").mkdir(exist_ok=True)
        return draft_dir

    def list_drafts(self) -> list[dict]:
        """List all drafts with their metadata."""
        drafts = []
        if not self.drafts_dir.exists():
            return drafts
        for d in sorted(self.drafts_dir.iterdir()):
            meta_file = d / "meta.yaml"
            if meta_file.exists():
                meta = self._read_yaml(meta_file)
                meta["_dir"] = str(d)
                drafts.append(meta)
        return drafts

    def get_draft(self, draft_id: str) -> dict | None:
        """Get a specific draft by ID (prefix match)."""
        if not self.drafts_dir.exists():
            return None
        for d in self.drafts_dir.iterdir():
            if d.name.startswith(draft_id):
                meta_file = d / "meta.yaml"
                if meta_file.exists():
                    meta = self._read_yaml(meta_file)
                    meta["_dir"] = str(d)
                    return meta
        return None

    def get_draft_dir(self, draft_id: str) -> Path | None:
        """Get the directory for a draft by ID (prefix match)."""
        if not self.drafts_dir.exists():
            return None
        for d in self.drafts_dir.iterdir():
            if d.name.startswith(draft_id):
                return d
        return None

    def update_draft_meta(self, draft_id: str, updates: dict):
        """Update fields in a draft's meta.yaml."""
        draft_dir = self.get_draft_dir(draft_id)
        if draft_dir is None:
            return
        meta_file = draft_dir / "meta.yaml"
        meta = self._read_yaml(meta_file) or {}
        meta.update(updates)
        self._write_yaml(meta_file, meta)

    # --- Published ---

    def add_published(self, record: dict):
        published = self._read_yaml(self.published_file) or []
        published.append(record)
        self._write_yaml(self.published_file, published)

    # --- Helpers ---

    def _read_yaml(self, path: Path):
        if not path.exists():
            return None
        with open(path) as f:
            return yaml.safe_load(f)

    def _write_yaml(self, path: Path, data):
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


# Fix import for ensure_initialized
import click
