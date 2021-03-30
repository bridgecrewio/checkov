from checkov.terraform.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from networkx.classes.digraph import DiGraph
from networkx import edge_dfs
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType


class ConnectionExistsSolver(BaseConnectionSolver):
    operator = 'exists'

    def __init__(self, resource_types, connected_resources_types, vertices_under_resource_types=None, vertices_under_connected_resources_types=None):
        super().__init__(resource_types, connected_resources_types, vertices_under_resource_types, vertices_under_connected_resources_types)

    def run(self, graph_connector: DiGraph):
        passed, failed = [], []
        for u, v in edge_dfs(graph_connector):
            origin_attributes = graph_connector.nodes(data=True)[u]
            destination_attributes = graph_connector.nodes(data=True)[v]
            origin_type = origin_attributes.get(CustomAttributes.RESOURCE_TYPE)
            destination_type = destination_attributes.get(CustomAttributes.RESOURCE_TYPE)
            if self.is_associated_edge(origin_type, destination_type):
                passed.extend([origin_attributes, destination_attributes])
            destination_block_type = destination_attributes.get(CustomAttributes.BLOCK_TYPE)
            if destination_block_type == BlockType.OUTPUT.value:
                try:
                    output_edges = graph_connector.edges(v, data=True)
                    _, output_destination, _ = next(iter(output_edges))
                    output_destination = graph_connector.nodes(data=True)[output_destination]
                    output_destination_type = output_destination.get(CustomAttributes.RESOURCE_TYPE)
                    if self.is_associated_edge(origin_type, output_destination_type):
                        passed.extend([origin_attributes, output_destination])
                except StopIteration:
                    continue
        for v, v_data in graph_connector.nodes(data=True):
            v_type = v_data.get(CustomAttributes.RESOURCE_TYPE)
            if self.is_associated_vertex(v_type):
                v_degree = graph_connector.degree(v)
                if v_degree == 0:
                    failed.append(v_data)
                else:
                    is_associated = False
                    for s, t, _ in graph_connector.edges(v, data=True):
                        s_attributes = graph_connector.nodes(data=True)[s]
                        t_attributes = graph_connector.nodes(data=True)[t]
                        s_type = s_attributes.get(CustomAttributes.RESOURCE_TYPE)
                        t_type = t_attributes.get(CustomAttributes.RESOURCE_TYPE)
                        if self.is_associated_edge(s_type, t_type):
                            is_associated = True
                    if not is_associated:
                        failed.append(v_data)
        return passed, failed
