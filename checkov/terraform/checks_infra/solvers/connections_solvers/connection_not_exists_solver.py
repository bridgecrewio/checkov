from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.connections_solvers.connection_exists_solver import ConnectionExistsSolver


class ConnectionNotExistsSolver(ConnectionExistsSolver):
    operator = Operators.NOT_EXISTS

    def __init__(self, resource_types, connected_resources_types, vertices_under_resource_types=None, vertices_under_connected_resources_types=None):
        super().__init__(resource_types, connected_resources_types, vertices_under_resource_types, vertices_under_connected_resources_types)

    def get_operation(self, graph_connector):
        passed, failed = super(ConnectionNotExistsSolver, self).get_operation(graph_connector)
        return failed, passed
