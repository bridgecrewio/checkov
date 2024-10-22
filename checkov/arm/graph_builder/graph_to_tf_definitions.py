from __future__ import annotations

from pathlib import Path
from typing import Any

from checkov.arm.graph_builder.graph_components.blocks import ArmBlock


def convert_graph_vertices_to_tf_definitions(
    vertices: list[ArmBlock], root_folder: str | Path | None
) -> tuple[dict[Path, Any], dict[str, dict[str, Any]]]:
    # TODO
    pass
