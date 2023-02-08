from __future__ import annotations

import logging
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
    NotIntersectsAttributeSolver,
    EqualsIgnoreCaseAttributeSolver,
    NotEqualsIgnoreCaseAttributeSolver,
    RangeIncludesAttributeSolver,
    RangeNotIncludesAttributeSolver,
    NumberOfWordsEqualsAttributeSolver,
    NumberOfWordsNotEqualsAttributeSolver,
    NumberOfWordsGreaterThanAttributeSolver,
    NumberOfWordsGreaterThanOrEqualAttributeSolver,
    NumberOfWordsLessThanAttributeSolver,
    NumberOfWordsLessThanOrEqualAttributeSolver,
    NotWithinAttributeSolver,
)
from checkov.common.checks_infra.solvers.connections_solvers.connection_one_exists_solver import \
    ConnectionOneExistsSolver
from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver
from checkov.common.util.type_forcers import force_list

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
    "not_within": NotWithinAttributeSolver,
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
    "not_intersects": NotIntersectsAttributeSolver,
    "equals_ignore_case": EqualsIgnoreCaseAttributeSolver,
    "not_equals_ignore_case": NotEqualsIgnoreCaseAttributeSolver,
    "range_includes": RangeIncludesAttributeSolver,
    "range_not_includes": RangeNotIncludesAttributeSolver,
    "number_of_words_equals": NumberOfWordsEqualsAttributeSolver,
    "number_of_words_not_equals": NumberOfWordsNotEqualsAttributeSolver,
    "number_of_words_greater_than": NumberOfWordsGreaterThanAttributeSolver,
    "number_of_words_greater_than_or_equal": NumberOfWordsGreaterThanOrEqualAttributeSolver,
    "number_of_words_less_than_or_equal": NumberOfWordsLessThanOrEqualAttributeSolver,
    "number_of_words_less_than": NumberOfWordsLessThanAttributeSolver,
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


class GraphCheckParser(BaseGraphCheckParser):
    def validate_check_config(self, file_path: str, raw_check: dict[str, dict[str, Any]]) -> bool:
        missing_fields = []

        # check existence of metadata block
        if "metadata" in raw_check:
            metadata = raw_check["metadata"]
            if "id" not in metadata:
                missing_fields.append("metadata.id")
            if "name" not in metadata:
                missing_fields.append("metadata.name")
            if "category" not in metadata:
                missing_fields.append("metadata.category")
        else:
            missing_fields.extend(("metadata.id", "metadata.name", "metadata.category"))

        # check existence of definition block
        if "definition" not in raw_check:
            missing_fields.append("definition")

        if missing_fields:
            logging.warning(f"Custom policy {file_path} is missing required fields {', '.join(missing_fields)}")
            return False

        # check if definition block is not obviously invalid
        definition = raw_check["definition"]
        if not isinstance(definition, (list, dict)):
            logging.warning(
                f"Custom policy {file_path} has an invalid 'definition' block type '{type(definition).__name__}', "
                "needs to be either a 'list' or 'dict'"
            )
            return False

        return True

    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> BaseGraphCheck:
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

    def _parse_raw_check(self, raw_check: Dict[str, Any], resources_types: Optional[List[str]]) -> BaseGraphCheck:
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
        }

        solver = type_to_solver.get(check.type)  # type:ignore[arg-type]  # if not str will return None
        if not solver:
            raise NotImplementedError(f"solver type {check.type} with operator {check.operator} is not supported")
        return solver


class NXGraphCheckParser(GraphCheckParser):
    # TODO: delete after downstream adjustments
    pass


def get_complex_operator(raw_check: Dict[str, Any]) -> Optional[str]:
    for operator in operators_to_complex_solver_classes.keys():
        if raw_check.get(operator):
            return operator
    return None
