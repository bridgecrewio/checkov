from pathlib import Path


def test_graph_policies_packaging_requirements() -> None:
    """Checks, if all graph_checks folder have a __init__.py file"""

    root_dir = Path(__file__).parents[4]

    for graph_dir in root_dir.rglob("graph_checks"):
        if ".mypy_cache" in graph_dir.parts:
            # skip paths, which are related to mypy
            continue

        assert (graph_dir / "__init__.py").exists()
