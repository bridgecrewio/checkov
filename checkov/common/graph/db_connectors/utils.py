from typing import Any

from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector


def set_db_connector_by_graph_framework(graph_framework: str) -> Any:
    if graph_framework == 'NETWORKX':
        return NetworkxConnector()
    elif graph_framework == 'IGRAPH':
        return IgraphConnector()
    elif graph_framework == 'RUSTWORKX':
        return RustworkxConnector()
    return None
