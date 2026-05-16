from datetime import datetime
from pathlib import Path


class ObsidianVaultManager:
    """Persistent creative memory vault."""

    def __init__(self, vault_root: str):
        self.vault_root = Path(vault_root)

    def initialize(self):
        folders = [
            "projects",
            "storyboards",
            "visual_dna",
            "runtime_logs",
            "winner_patterns",
            "provider_runtime",
            "memory_graph",
        ]

        for folder in folders:
            (self.vault_root / folder).mkdir(parents=True, exist_ok=True)

    def save_storyboard(self, project_id: str, markdown: str):
        path = self.vault_root / "storyboards" / f"{project_id}.md"

        payload = f"""\
# Storyboard

Project: {project_id}
Generated: {datetime.utcnow().isoformat()}

{markdown}
"""

        path.write_text(payload, encoding="utf-8")
        return str(path)
