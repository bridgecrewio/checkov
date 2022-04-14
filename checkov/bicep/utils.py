from __future__ import annotations

from pathlib import Path


def get_scannable_file_paths(root_folder: str | Path | None = None, files: list[str] | None = None) -> set[Path]:
    """Finds Bicep files"""

    file_paths: set[Path] = set()

    if root_folder:
        root_path = Path(root_folder)
        file_paths = {file_path for file_path in root_path.rglob("*.bicep")}
    if files:
        for file in files:
            if file.endswith(".bicep"):
                file_paths.add(Path(file))

    return file_paths


def clean_file_path(file_path: Path) -> Path:
    path_parts = [part for part in file_path.parts if part not in (".", "..")]

    return Path(*path_parts)
