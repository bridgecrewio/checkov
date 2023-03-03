from __future__ import annotations

import itertools
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.common.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraph


class ComplexConnectionSolver(BaseConnectionSolver):
    def __init__(self, solvers: Optional[List[BaseSolver]], operator: str) -> None:
        self.solver_type = SolverType.COMPLEX_CONNECTION
        self.solvers = solvers if solvers else []
        self.operator = operator

        resource_types = set()
        connected_resources_types = set()
        for sub_solver in self.solvers:
            if isinstance(sub_solver, BaseConnectionSolver):
                resource_types.update(sub_solver.resource_types)
                connected_resources_types.update(sub_solver.connected_resources_types)
            elif isinstance(sub_solver, BaseAttributeSolver):
                resource_types.update(sub_solver.resource_types)

        super().__init__(list(resource_types), list(connected_resources_types))

    @staticmethod
    def get_check_identifier(check: Dict[str, Any]) -> Tuple[str, str, Optional[Any]]:
        return check[CustomAttributes.ID], check[CustomAttributes.FILE_PATH], check.get(CustomAttributes.TF_RESOURCE_ADDRESS)

    @staticmethod
    def filter_duplicates(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return list({(ComplexConnectionSolver.get_check_identifier(check)): check for check in checks}.values())

    def filter_results(
        self, passed: List[Dict[str, Any]], failed: List[Dict[str, Any]], unknown: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        filter_solvers = [sub_solver for sub_solver in self.solvers if isinstance(sub_solver, BaseFilterSolver)]
        for sub_solver in filter_solvers:
            filter_pred = sub_solver._get_operation()
            passed = list(filter(filter_pred, passed))
            failed = list(filter(filter_pred, failed))
            unknown = list(filter(filter_pred, unknown))
        passed = self.filter_duplicates(passed)
        failed = self.filter_duplicates(failed)
        unknown = self.filter_duplicates(unknown)
        return passed, failed, unknown

    def get_sorted_connection_solvers(self) -> List[BaseConnectionSolver]:
        connection_solvers = [sub_solver for sub_solver in self.solvers if isinstance(sub_solver, BaseConnectionSolver)]
        filter_solvers = [sub_solver for sub_solver in self.solvers if isinstance(sub_solver, BaseFilterSolver)]

        resource_types_to_filter = []
        for filter_solver in filter_solvers:
            if filter_solver.attribute == "resource_type":
                resource_types_to_filter.extend(filter_solver.value)

        sorted_connection_solvers = []
        connection_solvers_with_filtered_resource_types = []
        for connection_solver in connection_solvers:
            if any(
                r in resource_types_to_filter
                for r in itertools.chain(connection_solver.resource_types, connection_solver.connected_resources_types)
            ):
                connection_solvers_with_filtered_resource_types.append(connection_solver)
            else:
                sorted_connection_solvers.append(connection_solver)

        sorted_connection_solvers.extend(connection_solvers_with_filtered_resource_types)
        return sorted_connection_solvers

    def run_attribute_solvers(self, graph_connector: LibraryGraph) -> \
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        attribute_solvers = [
            sub_solver
            for sub_solver in self.solvers
            if isinstance(sub_solver, (BaseAttributeSolver, BaseComplexSolver))
        ]
        passed_attributes, failed_attributes, unknown_attributes = [], [], []
        for attribute_solver in attribute_solvers:
            passed_solver, failed_solver, unknown_solver = attribute_solver.run(graph_connector)
            passed_attributes.extend(passed_solver)
            failed_attributes.extend(failed_solver)
            unknown_attributes.extend(unknown_solver)

        return passed_attributes, failed_attributes, unknown_attributes
