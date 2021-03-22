from checkov.graph.checks.checks_infra.enums import SolverType
from checkov.graph.checks.checks_infra.solvers.base_solver import BaseSolver


class BaseComplexSolver(BaseSolver):
    operator = ''

    def __init__(self, queries, resource_types):
        if queries is None:
            queries = []
        self.queries = queries
        self.resource_types = resource_types
        super().__init__(SolverType.COMPLEX)

    def get_operation(self, *args, **kwargs):
        predicates = []
        for i, query in enumerate(self.queries):
            predicates.append(query.get_operation(args[0]))
        return self._get_operation(*predicates)

    def _get_operation(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_negative_op(self, *args):
        return not self._get_operation(args)

    def run(self, graph_connector):
        all_vertices_resource_types = [data for _, data in graph_connector.nodes(data=True) if
                                       self.resource_type_pred(data)]
        passed_vertices = [data for data in all_vertices_resource_types if self.get_operation(data)]
        failed_vertices = [resource for resource in all_vertices_resource_types if resource not in passed_vertices]
        return passed_vertices, failed_vertices

    def resource_type_pred(self, v):
        return len(self.resource_types) == 0 or v.get('resource_type') in self.resource_types
