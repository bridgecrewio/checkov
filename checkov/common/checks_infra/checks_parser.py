from __future__ import annotations

from typing import Dict, Any, List, Optional, Type, TYPE_CHECKING

from checkov.common.checks_infra.solvers import (
    EqualsAttributeSolver,
    NotEqualsAttributeSolver,
    RegexMatchAttributeSolver,
    NotRegexMatchAttributeSolver,
    ExistsAttributeSolver,
    AnyResourceSolver,
    ContainsAttributeSolver,
    NotExistsAttributeSolver,
    WithinAttributeSolver,
    NotContainsAttributeSolver,
    StartingWithAttributeSolver,
    NotStartingWithAttributeSolver,
    EndingWithAttributeSolver,
    NotEndingWithAttributeSolver,
    AndSolver,
    OrSolver,
    NotSolver,
    ConnectionExistsSolver,
    ConnectionNotExistsSolver,
    AndConnectionSolver,
    OrConnectionSolver,
    WithinFilterSolver,
    GreaterThanAttributeSolver,
    GreaterThanOrEqualAttributeSolver,
    LessThanAttributeSolver,
    LessThanOrEqualAttributeSolver,
    SubsetAttributeSolver,
    NotSubsetAttributeSolver,
    IsEmptyAttributeSolver,
    IsNotEmptyAttributeSolver,
    LengthEqualsAttributeSolver,
    LengthNotEqualsAttributeSolver,
    LengthGreaterThanAttributeSolver,
    LengthLessThanAttributeSolver,
    LengthLessThanOrEqualAttributeSolver,
    LengthGreaterThanOrEqualAttributeSolver,
    IsTrueAttributeSolver,
    IsFalseAttributeSolver,
    IntersectsAttributeSolver,
    NotIntersectsAttributeSolver
)
from checkov.common.bridgecrew.integration_features.features.attribute_resource_types_integration import integration as attribute_resource_type_integration
from checkov.common.checks_infra.solvers.connections_solvers.connection_one_exists_solver import \
    ConnectionOneExistsSolver
from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.util.type_forcers import force_list, force_list_or_set

if TYPE_CHECKING:
    from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
    from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
    from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
    from checkov.common.checks_infra.solvers.connections_solvers.complex_connection_solver import ComplexConnectionSolver
    from checkov.common.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver


operators_to_attributes_solver_classes: dict[str, Type[BaseAttributeSolver]] = {
    "equals": EqualsAttributeSolver,
    "not_equals": NotEqualsAttributeSolver,
    "regex_match": RegexMatchAttributeSolver,
    "not_regex_match": NotRegexMatchAttributeSolver,
    "exists": ExistsAttributeSolver,
    "any": AnyResourceSolver,
    "contains": ContainsAttributeSolver,
    "not_exists": NotExistsAttributeSolver,
    "within": WithinAttributeSolver,
    "not_contains": NotContainsAttributeSolver,
    "starting_with": StartingWithAttributeSolver,
    "not_starting_with": NotStartingWithAttributeSolver,
    "ending_with": EndingWithAttributeSolver,
    "not_ending_with": NotEndingWithAttributeSolver,
    "greater_than": GreaterThanAttributeSolver,
    "greater_than_or_equal": GreaterThanOrEqualAttributeSolver,
    "less_than": LessThanAttributeSolver,
    "less_than_or_equal": LessThanOrEqualAttributeSolver,
    "subset": SubsetAttributeSolver,
    "not_subset": NotSubsetAttributeSolver,
    "is_empty": IsEmptyAttributeSolver,
    "is_not_empty": IsNotEmptyAttributeSolver,
    "length_equals": LengthEqualsAttributeSolver,
    "length_not_equals": LengthNotEqualsAttributeSolver,
    "length_greater_than": LengthGreaterThanAttributeSolver,
    "length_greater_than_or_equal": LengthGreaterThanOrEqualAttributeSolver,
    "length_less_than": LengthLessThanAttributeSolver,
    "length_less_than_or_equal": LengthLessThanOrEqualAttributeSolver,
    "is_true": IsTrueAttributeSolver,
    "is_false": IsFalseAttributeSolver,
    "intersects": IntersectsAttributeSolver,
    "not_intersects": NotIntersectsAttributeSolver
}

operators_to_complex_solver_classes: dict[str, Type[BaseComplexSolver]] = {
    "and": AndSolver,
    "or": OrSolver,
    "not": NotSolver,
}

operator_to_connection_solver_classes: dict[str, Type[BaseConnectionSolver]] = {
    "exists": ConnectionExistsSolver,
    "one_exists": ConnectionOneExistsSolver,
    "not_exists": ConnectionNotExistsSolver
}

operator_to_complex_connection_solver_classes: dict[str, Type[ComplexConnectionSolver]] = {
    "and": AndConnectionSolver,
    "or": OrConnectionSolver,
}

operator_to_filter_solver_classes: dict[str, Type[BaseFilterSolver]] = {
    "within": WithinFilterSolver,
}

condition_type_to_solver_type = {
    "": SolverType.ATTRIBUTE,
    "attribute": SolverType.ATTRIBUTE,
    "connection": SolverType.CONNECTION,
    "filter": SolverType.FILTER,
}

JSONPATH_PREFIX = "jsonpath_"


class NXGraphCheckParser(BaseGraphCheckParser):
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> BaseGraphCheck:
        policy_definition = raw_check.get("definition", {})

        metadata = raw_check.get("metadata", {})
        provider = metadata.get("scope", {}).get("provider")

        check = self._parse_raw_check(policy_definition, provider)

        check.id = metadata.get("id", "")
        check.name = metadata.get("name", "")
        check.category = metadata.get("category", "")
        check.frameworks = metadata.get("frameworks", [])
        check.guideline = metadata.get("guideline")
        check.provider = provider

        solver = self.get_check_solver(check)
        check.set_solver(solver)

        return check

    def _parse_raw_check(self, raw_check: Dict[str, Any], provider: Optional[str]) -> BaseGraphCheck:
        check = BaseGraphCheck()
        complex_operator = get_complex_operator(raw_check)
        if complex_operator:
            check.type = SolverType.COMPLEX
            check.operator = complex_operator
            sub_solvers = raw_check.get(complex_operator, [])

            # this allows flexibility for specifying the child conditions, and makes "not" more intuitive by
            # not requiring an actual list
            if isinstance(sub_solvers, dict):
                sub_solvers = [sub_solvers]

            for sub_solver in sub_solvers:
                check.sub_checks.append(self._parse_raw_check(sub_solver, provider))

            # conditions with enumerated resource types will have them as a list. conditions where `all` is replaced with the
            # actual list of resource for the attribute (e.g. tags) will have them as a set, because that logic works best with sets
            # here, they will end up as a list in the policy resource types
            resources_types_of_sub_solvers = [
                force_list_or_set(q.resource_types) for q in check.sub_checks if q is not None and q.resource_types is not None
            ]
            if resources_types_of_sub_solvers:
                check.resource_types = list(set().union(*resources_types_of_sub_solvers))
            else:
                check.resource_types = []
            if any(q.type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION] for q in check.sub_checks):
                check.type = SolverType.COMPLEX_CONNECTION

        else:
            resource_type = raw_check.get("resource_types", [])
            if (
                    not resource_type
                    or (isinstance(resource_type, str) and resource_type.lower() == "all")
                    or (isinstance(resource_type, list) and resource_type[0].lower() == "all")
            ):
                resource_types_for_attribute = attribute_resource_type_integration.get_attribute_resource_types(raw_check, provider)
                check.resource_types = resource_types_for_attribute or []
            else:
                check.resource_types = resource_type

            connected_resources_type = raw_check.get("connected_resource_types", [])

            # TODO this code has a capital 'All', so I am pretty sure this rarely gets used. need to validate the use case
            # and make it work with the resource types from the platform if needed
            if connected_resources_type == ["All"] or connected_resources_type == "all":
                check.connected_resources_types = []
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
        }

        solver = type_to_solver.get(check.type)  # type:ignore[arg-type]  # if not str will return None
        if not solver:
            raise NotImplementedError(f"solver type {check.type} with operator {check.operator} is not supported")
        return solver


def get_complex_operator(raw_check: Dict[str, Any]) -> Optional[str]:
    for operator in operators_to_complex_solver_classes.keys():
        if raw_check.get(operator):
            return operator
    return None
