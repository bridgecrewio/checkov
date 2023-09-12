from typing import Any

from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector


def set_db_connector_by_graph_framework(graph_framework: str) -> Any:
    if graph_framework == 'NETWORKX':
        db_connector = NetworkxConnector()
    elif graph_framework == 'IGRAPH':
        db_connector = IgraphConnector()
    elif graph_framework == 'RUSTWORKX':
        db_connector = RustworkxConnector()
    else:
        return None
    return db_connector
