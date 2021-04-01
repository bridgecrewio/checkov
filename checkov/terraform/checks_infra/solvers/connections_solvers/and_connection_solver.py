from networkx.classes.digraph import DiGraph

from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


class AndConnectionSolver(ComplexConnectionSolver):
    operator = Operators.AND

    def __init__(self, solvers, operator):
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph):
        passed_attributes, failed_attributes = self.run_attribute_solvers(graph_connector)
        passed_attributes = [p for p in passed_attributes if
                             p[CustomAttributes.ID] not in [f[CustomAttributes.ID] for f in failed_attributes]]
        passed, failed = passed_attributes, failed_attributes
        connection_solvers = self.get_sorted_connection_solvers()
        passed_connections, failed_connections = [], []
        for connection_solver in connection_solvers:
            connection_solver.set_vertices(graph_connector, failed_attributes+failed_connections)
            passed_solver, failed_solver = connection_solver.get_operation(graph_connector)
            passed_connections.extend(passed_solver)
            failed_connections.extend(failed_solver)
            passed_connections = [p for p in passed_connections if
                      p[CustomAttributes.ID] not in [f[CustomAttributes.ID] for f in failed_connections]]

        passed.extend(passed_connections)
        failed.extend(failed_connections)
        passed = [p for p in passed if
                              p[CustomAttributes.ID] not in [f[CustomAttributes.ID] for f in failed]]
        passed = [p for p in passed if
                  p[CustomAttributes.ID] in [pt[CustomAttributes.ID] for pt in passed_attributes] and p[
                      CustomAttributes.ID] in [pt[CustomAttributes.ID] for pt in passed_connections]]

        return self.filter_results(passed, failed)

    def _get_operation(self, *args, **kwargs):
        pass



