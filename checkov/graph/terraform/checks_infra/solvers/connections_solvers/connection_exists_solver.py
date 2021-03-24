from checkov.graph.terraform.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver


class ConnectionExistsSolver(BaseConnectionSolver):
    operator = 'exists'

    def __init__(self, resource_types, connected_resources_types, vertices_under_resource_types=None, vertices_under_connected_resources_types=None):
        super().__init__(resource_types, connected_resources_types, vertices_under_resource_types, vertices_under_connected_resources_types)

    def run_query(self, graph_connector):
        # TODO
        raise NotImplementedError
