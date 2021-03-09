from checkov.graph.checks.checks_infra.base_check import BaseGraphCheck
from checkov.graph.checks.checks_infra.base_parser import BaseGraphCheckParser
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.any_attribute_solver import AnyResourceSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.array_contains_attribute_solver import ArrayContainsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.array_not_contains_attribute_solver import ArrayNotContainsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.ending_with_attribute_solver import \
    EndingWithAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.equals_attribute_solver import EqualsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.exists_attribute_solver import ExistsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.not_ending_with_attribute_solver import \
    NotEndingWithAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.not_equals_attribute_solver import NotEqualsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.not_exists_attribute_solver import NotExistsAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.within_attribute_solver import WithinAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.starting_with_attribute_solver import StartingWithAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.not_starting_with_attribute_solver import NotStartingWithAttributeSolver
from checkov.graph.terraform.checks.checks_infra.solvers.complex_queries.and_solver import AndSolver
from checkov.graph.terraform.checks.checks_infra.solvers.complex_queries.or_solver import OrSolver
from checkov.graph.terraform.checks.checks_infra.solvers.connections_queries.and_connection_solver import AndConnectionSolver
from checkov.graph.terraform.checks.checks_infra.solvers.connections_queries.connection_exists_solver import ConnectionExistsSolver
from checkov.graph.terraform.checks.checks_infra.solvers.connections_queries.connection_not_exists_solver import ConnectionNotExistsSolver
from checkov.graph.terraform.checks.checks_infra.solvers.connections_queries.or_connection_solver import OrConnectionSolver
from checkov.graph.checks.checks_infra.enums import SolverType
from checkov.graph.terraform.checks.checks_infra.solvers.filter_queries.within_filter_solver import WithinFilterSolver


operators_to_attributes_query_classes = {
    'equals': EqualsAttributeSolver,
    'not_equals': NotEqualsAttributeSolver,
    'exists': ExistsAttributeSolver,
    'any': AnyResourceSolver,
    'contains': ArrayContainsAttributeSolver,
    'not_exists': NotExistsAttributeSolver,
    'within': WithinAttributeSolver,
    'not_contains': ArrayNotContainsAttributeSolver,
    'starting_with': StartingWithAttributeSolver,
    'not_starting_with': NotStartingWithAttributeSolver,
    'ending_with': EndingWithAttributeSolver,
    'not_ending_with': NotEndingWithAttributeSolver
}

operators_to_complex_query_classes = {
    'and': AndSolver,
    'or': OrSolver,
}

operator_to_connection_query_classes = {
    'exists': ConnectionExistsSolver,
    'not_exists': ConnectionNotExistsSolver
}

operator_to_complex_connection_query_classes = {
    'and': AndConnectionSolver,
    'or': OrConnectionSolver
}

operator_to_filter_query_classes = {
    'within': WithinFilterSolver,
}


condition_type_to_query_type = {
    '': SolverType.ATTRIBUTE,
    'attribute': SolverType.ATTRIBUTE,
    'connection': SolverType.CONNECTION,
    'filter': SolverType.FILTER
}


class NXGraphCheckParser(BaseGraphCheckParser):
    def parse_raw_check(self, raw_check, **kwargs):
        policy_query = raw_check.get("query")
        check = self._parse_raw_check(policy_query, kwargs.get("resources_types"))
        check.id = raw_check.get("metadata", {}).get("id")
        solver = self.get_check_solver(check)
        check.set_solver(solver)

    def _parse_raw_check(self, raw_check, resources_types):
        check = BaseGraphCheck()
        complex_operator = get_complex_operator(raw_check)
        if complex_operator:
            check.type = SolverType.COMPLEX
            check.operator = complex_operator
            sub_queries = raw_check.get(complex_operator)
            for sub_query in sub_queries:
                check.sub_checks.append(self.parse_raw_check(sub_query))
            resources_types_of_sub_queries = [q.resource_types for q in check.sub_checks]
            check.resource_types = list(set(sum(resources_types_of_sub_queries, [])))
            if any(q.type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION] for q in check.sub_checks):
                check.type = SolverType.COMPLEX_CONNECTION

        else:
            resource_type = raw_check.get("resource_types", [])
            if resource_type == ['All'] or resource_type == 'all' or not resource_type:
                check.resource_types = resources_types
            else:
                check.resource_types = resource_type

            connected_resources_type = raw_check.get('connected_resource_types', [])
            if connected_resources_type == ['All'] or connected_resources_type == 'all':
                check.connected_resources_types = resources_types
            else:
                check.connected_resources_types = connected_resources_type

            condition_type = raw_check.get('cond_type', '')
            check.type = condition_type_to_query_type.get(condition_type)
            if condition_type == '':
                check.operator = 'any'
            else:
                check.operator = raw_check.get('operator')
            check.attribute = raw_check.get('attribute')
            check.attribute_value = raw_check.get('value')

        return check

    def get_check_solver(self, check):
        sub_queries_solvers = []
        if check.sub_checks:
            sub_queries_solvers = []
            for sub_query in check.sub_checks:
                sub_queries_solvers.append(self.get_check_solver(sub_query))

        type_to_solver = {
            SolverType.COMPLEX_CONNECTION: operator_to_complex_connection_query_classes.get(check.operator, lambda *args: None)(sub_queries_solvers, check.operator),
            SolverType.COMPLEX: operators_to_complex_query_classes.get(check.operator, lambda *args: None)(sub_queries_solvers, check.resource_types),
            SolverType.ATTRIBUTE: operators_to_attributes_query_classes.get(check.operator, lambda *args: None)(check.resource_types, check.attribute, check.attribute_value),
            SolverType.CONNECTION: operator_to_connection_query_classes.get(check.operator, lambda *args: None)(check.resource_types, check.connected_resources_types),
            SolverType.FILTER: operator_to_filter_query_classes.get(check.operator, lambda *args: None)(check.resource_types, check.attribute, check.attribute_value)
        }

        solver = type_to_solver.get(check.type)
        if not solver:
            raise NotImplementedError(f"query type {check.type} with operator {check.operator} is not supported")
        return solver


def get_complex_operator(raw_check):
    for operator in operators_to_complex_query_classes.keys():
        if raw_check.get(operator):
            return operator
    return None

