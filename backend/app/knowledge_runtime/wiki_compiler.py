from datetime import datetime
from pathlib import Path


class WikiCompiler:
    """Compile knowledge once and reuse it."""

    def compile_project_memory(self, project_id: str, content: str, output_dir: str):
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        md = root / f"{project_id}.md"

        compiled = f"""\
# Project Knowledge

## Project ID
{project_id}

## Generated
{datetime.utcnow().isoformat()}

## Persistent Knowledge
{content}
"""

        md.write_text(compiled, encoding="utf-8")

        return {
            "project_id": project_id,
            "markdown_path": str(md),
            "status": "compiled",
        }
