from __future__ import annotations

from typing import Dict, Any, Type, TYPE_CHECKING

from checkov.common.checks_infra.solvers import (
    AndSolver,
    OrSolver,
)

from checkov.policies3d.checks_infra.base_parser import Base3dPolicyCheckParser
from checkov.policies3d.checks_infra.base_check import Base3dPolicyCheck

if TYPE_CHECKING:
    from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver

operators_to_solver_classes: dict[str, Type[BaseComplexSolver]] = {
    "iac": AndSolver,
    "cve": OrSolver,
}


class Policy3dParser(Base3dPolicyCheckParser):
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        policy_definition = raw_check.get("definition", {})
        check = Base3dPolicyCheck()
        check.iac = policy_definition.get('iac')
        check.cve = policy_definition.get('cve')
        check.id = raw_check.get("metadata", {}).get("id", "")
        check.name = raw_check.get("metadata", {}).get("name", "")
        check.category = raw_check.get("metadata", {}).get("category", "")
        check.frameworks = raw_check.get("metadata", {}).get("frameworks", [])
        check.guideline = raw_check.get("metadata", {}).get("guideline")
        check.check_path = kwargs.get("check_path", "")
        # solver = self.get_check_solver(check)
        # check.set_solver(solver)

        return check

    # def get_check_solver(self, check: Base3dPolicyCheck) -> BaseSolver:
        # sub_solvers: List[BaseSolver] = []
        # if check.sub_checks:
        #     sub_solvers = []
        #     for sub_solver in check.sub_checks:
        #         sub_solvers.append(self.get_check_solver(sub_solver))
        #
        # type_to_solver = {
        #     SolverType.COMPLEX_CONNECTION: operator_to_complex_connection_solver_classes.get(
        #         check.operator, lambda *args: None
        #     )(sub_solvers, check.operator),
        #     SolverType.COMPLEX: operators_to_complex_solver_classes.get(check.operator, lambda *args: None)(
        #         sub_solvers, check.resource_types
        #     ),
        #     SolverType.ATTRIBUTE: self.get_solver_type_method(check),
        #     SolverType.CONNECTION: operator_to_connection_solver_classes.get(check.operator, lambda *args: None)(
        #         check.resource_types, check.connected_resources_types
        #     ),
        #     SolverType.FILTER: operator_to_filter_solver_classes.get(check.operator, lambda *args: None)(
        #         check.resource_types, check.attribute, check.attribute_value
        #     ),
        #     SolverType.VULNERABILITY: operator_tox
        # }
        #
        # solver = type_to_solver.get(check.type)  # type:ignore[arg-type]  # if not str will return None
        # if not solver:
        #     raise NotImplementedError(f"solver type {check.type} with operator {check.operator} is not supported")
        # return solver


# def get_complex_operator(raw_check: Dict[str, Any]) -> Optional[str]:
#     for operator in operators_to_complex_solver_classes.keys():
#         if raw_check.get(operator):
#             return operator
#     return None
