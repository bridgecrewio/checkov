from networkx.classes.digraph import DiGraph
from checkov.common.graph.checks_infra.enums import SolverType, Operators
from checkov.terraform.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


class OrConnectionSolver(ComplexConnectionSolver):
    operator = Operators.OR

    def __init__(self, solvers, operator):
        super().__init__(solvers, operator)

    def get_operation(self, graph_connector: DiGraph):
        passed_attributes, failed_attributes = self.run_attribute_solvers(graph_connector)
        failed_attributes = [f for f in failed_attributes if
                             f[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed_attributes]]
        passed, failed = passed_attributes, failed_attributes
        connection_solvers = [sub_solver for sub_solver in self.solvers if
                              sub_solver.solver_type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION]]
        passed_connections, failed_connections = [], []
        failed_by_hash = {}
        for connection_solver in connection_solvers:
            connection_solver.set_vertices(graph_connector, [])
            passed_solver, failed_solvers = connection_solver.get_operation(graph_connector)
            passed_connections.extend(passed_solver)
            for f in failed_solvers:
                if f[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed_connections]:
                    if not failed_by_hash.get(f[CustomAttributes.HASH]):
                        failed_by_hash[f[CustomAttributes.HASH]] = {"v": f, "count": 0}
                    failed_by_hash[f[CustomAttributes.HASH]]["count"] += 1

        for data in failed_by_hash.values():
            if data["count"] == len(connection_solvers) or data["v"] not in passed_connections:
                failed.append(data["v"])

        passed.extend(passed_connections)
        failed = [f for f in failed if
                  f[CustomAttributes.ID] not in [p[CustomAttributes.ID] for p in passed]]

        return self.filter_results(passed, failed)
