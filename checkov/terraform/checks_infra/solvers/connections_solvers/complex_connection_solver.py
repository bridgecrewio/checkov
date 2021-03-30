from checkov.common.graph.checks_infra.enums import SolverType
from checkov.terraform.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from networkx.classes.digraph import DiGraph

from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


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
            if sub_query.solver_type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION]:
                resource_types.extend(sub_query.resource_types)
                connected_resources_types.extend(sub_query.connected_resources_types)
        resource_types = list(set(resource_types))
        connected_resources_types = list(set(connected_resources_types))

        super().__init__(resource_types, connected_resources_types)

    def run(self, graph_connector: DiGraph):
        raise NotImplementedError

    @staticmethod
    def filter_duplicates(checks):
        return list({check[CustomAttributes.ID]: check for check in checks}.values())

    def filter_results(self, passed: list, failed: list):
        filters = []
        filter_queries = [sub_query for sub_query in self.queries if sub_query.solver_type == SolverType.FILTER]
        for sub_query in filter_queries:
            filters.append(sub_query._get_operation())
        if filters:
            for query_filter in filters:
                passed = list(filter(query_filter, passed))
                failed = list(filter(query_filter, failed))
        passed = self.filter_duplicates(passed)
        failed = self.filter_duplicates(failed)
        return passed, failed
