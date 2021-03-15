from checkov.graph.terraform.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.graph.checks.checks_infra.enums import SolverType


class ComplexConnectionSolver(BaseConnectionSolver):
    operator = ''

    def __init__(self, queries, operator):
        if queries is None:
            queries = []
        self.queries = queries
        self.operator = operator

        resource_types = []
        connected_resources_types = []
        for sub_query in self.queries:
            if sub_query.query_type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION]:
                resource_types.extend(sub_query.resource_types)
                connected_resources_types.extend(sub_query.connected_resources_types)
        resource_types = list(set(resource_types))
        connected_resources_types = list(set(connected_resources_types))

        super().__init__(resource_types, connected_resources_types)

    def run_query(self, graph_connector):
        # TODO
        raise NotImplementedError

    def get_operation(self, **kwargs):
        raise NotImplementedError

    def filter_results(self, traversal):
        raise NotImplementedError
