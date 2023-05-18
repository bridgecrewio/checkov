from __future__ import annotations

import logging
from typing import Dict, Any, TYPE_CHECKING

from checkov.common.graph.graph_builder import CustomAttributes

if TYPE_CHECKING:
    from igraph import Graph


def get_git_root_path(path: str) -> str:
    try:
        import git  # Local import to make sure we don't fail if `git` is not installed on computer
        git_repo = git.Repo(path, search_parent_directories=True)
        git_root = git_repo.git.rev_parse("--show-toplevel")
        return str(git_root)
    except Exception as e:
        logging.debug(f'Failed to reolve git root path with error: {e}')
        return ''


def serialize_to_json(igraph: Graph) -> Dict[str, Any]:
    nodes = []
    for i, vertex in enumerate(igraph.vs):
        attr = {k: v for k, v in vertex.attributes()['attr'].items() if v is not None}
        node = {'attr': attr, "id": vertex.attributes().get('block_index', i),
                "name": vertex.attributes().get('name', attr[CustomAttributes.HASH]),
                CustomAttributes.BLOCK_TYPE: vertex[CustomAttributes.BLOCK_TYPE],
                CustomAttributes.RESOURCE_TYPE: attr[CustomAttributes.RESOURCE_TYPE] if CustomAttributes.RESOURCE_TYPE in attr else None}
        nodes.append(node)

    links = [
        {
            "label": edge["label"],
            "source": edge.source,
            "target": edge.target
        }
        for edge in igraph.es
    ]

    graph_path = nodes[0]['attr'][CustomAttributes.FILE_PATH] if nodes else ''
    git_root_path = get_git_root_path(graph_path)  # Allows to compare a node with only its relative file path to the git root
    graph = {"graph_type": "igraph", "git_root_path": git_root_path, "nodes": nodes, "links": links}

    return graph
