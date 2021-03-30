from networkx.classes.digraph import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.terraform.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


class OrConnectionSolver(ComplexConnectionSolver):
    operator = 'or'

    def __init__(self, queries, operator):
        super().__init__(queries, operator)

    def run(self, graph_connector: DiGraph):
        passed, failed = [], []
        for sub_query in self.queries:
            if sub_query.solver_type in [SolverType.ATTRIBUTE, SolverType.CONNECTION]:
                sub_passed, sub_failed = sub_query.run(graph_connector)
                passed.extend(sub_passed)
                failed.extend(sub_failed)
                failed = [f for f in failed if f[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed]]
        return self.filter_results(passed, failed)
