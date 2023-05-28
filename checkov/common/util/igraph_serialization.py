from __future__ import annotations

from typing import Dict, Any, TYPE_CHECKING

from checkov.common.graph.graph_builder import CustomAttributes

if TYPE_CHECKING:
    from igraph import Graph


def serialize_to_json(igraph: Graph, absolute_root_folder: str = '') -> Dict[str, Any]:
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

    graph = {"graph_type": "igraph", "absolute_root_folder": absolute_root_folder, "nodes": nodes, "links": links}

    return graph
