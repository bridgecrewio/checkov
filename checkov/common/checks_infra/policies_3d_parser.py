from __future__ import annotations

from typing import Dict, Any, List, Optional, Type, TYPE_CHECKING

from .checks_parser import NXGraphCheckParser
from checkov.common.policies3d.checks_infra.base_check import Base3dPolicyCheck

class Policies3DParser(NXGraphCheckParser):
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        policy_definition = raw_check.get("definition", {})
        check = self._parse_raw_check(policy_definition, kwargs.get("resources_types"))
        check.id = raw_check.get("metadata", {}).get("id", "")
        check.name = raw_check.get("metadata", {}).get("name", "")
        check.category = raw_check.get("metadata", {}).get("category", "")
        check.frameworks = raw_check.get("metadata", {}).get("frameworks", [])
        check.guideline = raw_check.get("metadata", {}).get("guideline")
        check.check_path = kwargs.get("check_path", "")
        solver = self.get_check_solver(check)
        check.set_solver(solver)

        return check

    def _parse_raw_check(self, raw_check: Dict[str, Any], resources_types: Optional[List[str]]) -> Base3dPolicyCheck:
        check = Base3dPolicyCheck()
        complex_operator = get_complex_operator(raw_check)

            for sub_solver in sub_solvers:
                check.sub_checks.append(self._parse_raw_check(sub_solver, resources_types))
            resources_types_of_sub_solvers = [
                force_list(q.resource_types) for q in check.sub_checks if q is not None and q.resource_types is not None
            ]
            check.resource_types = list(set(sum(resources_types_of_sub_solvers, [])))
            if any(q.type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION] for q in check.sub_checks):
                check.type = SolverType.COMPLEX_CONNECTION

        else:
            resource_type = raw_check.get("resource_types", [])
            if (
                    not resource_type
                    or (isinstance(resource_type, str) and resource_type.lower() == "all")
                    or (isinstance(resource_type, list) and resource_type[0].lower() == "all")
            ):
                check.resource_types = resources_types or []
            else:
                check.resource_types = resource_type

            connected_resources_type = raw_check.get("connected_resource_types", [])
            if connected_resources_type == ["All"] or connected_resources_type == "all":
                check.connected_resources_types = resources_types or []
            else:
                check.connected_resources_types = connected_resources_type

            condition_type = raw_check.get("cond_type", "")
            check.type = condition_type_to_solver_type.get(condition_type)
            if condition_type == "":
                check.operator = "any"
            else:
                check.operator = raw_check.get("operator", "")
            check.attribute = raw_check.get("attribute")
            check.attribute_value = raw_check.get("value")

        return check

    @staticmethod
    def get_solver_type_method(check: BaseGraphCheck) -> Optional[BaseAttributeSolver]:
        check.is_jsonpath_check = check.operator.startswith(JSONPATH_PREFIX)
        if check.is_jsonpath_check:
            solver = check.operator.replace(JSONPATH_PREFIX, '')
        else:
            solver = check.operator

        return operators_to_attributes_solver_classes.get(solver, lambda *args: None)(
            check.resource_types, check.attribute, check.attribute_value, check.is_jsonpath_check
        )

    def get_check_solver(self, check: BaseGraphCheck) -> BaseSolver:
        sub_solvers: List[BaseSolver] = []
        if check.sub_checks:
            sub_solvers = []
            for sub_solver in check.sub_checks:
                sub_solvers.append(self.get_check_solver(sub_solver))

        type_to_solver = {
            SolverType.COMPLEX_CONNECTION: operator_to_complex_connection_solver_classes.get(
                check.operator, lambda *args: None
            )(sub_solvers, check.operator),
            SolverType.COMPLEX: operators_to_complex_solver_classes.get(check.operator, lambda *args: None)(
                sub_solvers, check.resource_types
            ),
            SolverType.ATTRIBUTE: self.get_solver_type_method(check),
            SolverType.CONNECTION: operator_to_connection_solver_classes.get(check.operator, lambda *args: None)(
                check.resource_types, check.connected_resources_types
            ),
            SolverType.FILTER: operator_to_filter_solver_classes.get(check.operator, lambda *args: None)(
                check.resource_types, check.attribute, check.attribute_value
            ),
            SolverType.VULNERABILITY: operator_tox
        }

        solver = type_to_solver.get(check.type)  # type:ignore[arg-type]  # if not str will return None
        if not solver:
            raise NotImplementedError(f"solver type {check.type} with operator {check.operator} is not supported")
        return solver
