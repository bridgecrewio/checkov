from typing import Dict, Any
from igraph import Graph as Igraph

from checkov.common.graph.graph_builder import CustomAttributes


def serialize_to_json(igraph: Igraph) -> Dict[str, Any]:
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

    graph = {"graph_type": "igraph", "nodes": nodes, "links": links}
    return graph
