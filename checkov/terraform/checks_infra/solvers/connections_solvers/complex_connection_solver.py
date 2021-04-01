from checkov.common.graph.checks_infra.enums import SolverType
from checkov.terraform.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver

from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes


class ComplexConnectionSolver(BaseConnectionSolver):
    def __init__(self, solvers, operator):
        self.solver_type = SolverType.COMPLEX_CONNECTION
        if solvers is None:
            solvers = []
        self.solvers = solvers
        self.operator = operator

        resource_types = []
        connected_resources_types = []
        for sub_solver in self.solvers:
            if sub_solver.solver_type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION]:
                resource_types.extend(sub_solver.resource_types)
                connected_resources_types.extend(sub_solver.connected_resources_types)
            elif sub_solver.solver_type in [SolverType.ATTRIBUTE]:
                resource_types.extend(sub_solver.resource_types)
        resource_types = list(set(resource_types))
        connected_resources_types = list(set(connected_resources_types))

        super().__init__(resource_types, connected_resources_types)

    @staticmethod
    def filter_duplicates(checks):
        return list({check[CustomAttributes.ID]: check for check in checks}.values())

    def filter_results(self, passed: list, failed: list):
        filters = []
        filter_solvers = [sub_solver for sub_solver in self.solvers if sub_solver.solver_type == SolverType.FILTER]
        for sub_solver in filter_solvers:
            filters.append(sub_solver._get_operation())
        if filters:
            for filter_pred in filters:
                passed = list(filter(filter_pred, passed))
                failed = list(filter(filter_pred, failed))
        passed = self.filter_duplicates(passed)
        failed = self.filter_duplicates(failed)
        return passed, failed

    def get_sorted_connection_solvers(self):
        connection_solvers = [sub_solver for sub_solver in self.solvers if
                              sub_solver.solver_type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION]]
        filter_solvers = [sub_solver for sub_solver in self.solvers if sub_solver.solver_type == SolverType.FILTER]

        resource_types_to_filter = []
        for filter_solver in filter_solvers:
            if filter_solver.attribute == 'resource_type':
                resource_types_to_filter.extend(filter_solver.value)

        sorted_connection_solvers = []
        connection_solvers_with_filtered_resource_types = []
        for connection_solver in connection_solvers:
            if any(r in resource_types_to_filter for r in connection_solver.resource_types + connection_solver.connected_resources_types):
                connection_solvers_with_filtered_resource_types.append(connection_solver)
            else:
                sorted_connection_solvers.append(connection_solver)

        sorted_connection_solvers.extend(connection_solvers_with_filtered_resource_types)
        return sorted_connection_solvers

    def run_attribute_solvers(self, graph_connector):
        attribute_solvers = [sub_solver for sub_solver in self.solvers if
                             sub_solver.solver_type in [SolverType.ATTRIBUTE, SolverType.COMPLEX]]
        passed_attributes, failed_attributes = [], []
        for attribute_solver in attribute_solvers:
            passed_solver, failed_solver = attribute_solver.run(graph_connector)
            passed_attributes.extend(passed_solver)
            failed_attributes.extend(failed_solver)
        return passed_attributes, failed_attributes
