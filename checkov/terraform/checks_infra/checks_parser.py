from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.graph.checks_infra.enums import SolverType
from checkov.terraform.checks_infra.solvers import *

operators_to_attributes_solver_classes = {
    'equals': EqualsAttributeSolver,
    'not_equals': NotEqualsAttributeSolver,
    'exists': ExistsAttributeSolver,
    'any': AnyResourceSolver,
    'contains': ContainsAttributeSolver,
    'not_exists': NotExistsAttributeSolver,
    'within': WithinAttributeSolver,
    'not_contains': NotContainsAttributeSolver,
    'starting_with': StartingWithAttributeSolver,
    'not_starting_with': NotStartingWithAttributeSolver,
    'ending_with': EndingWithAttributeSolver,
    'not_ending_with': NotEndingWithAttributeSolver
}

operators_to_complex_solver_classes = {
    'and': AndSolver,
    'or': OrSolver,
}

operator_to_connection_solver_classes = {
    'exists': ConnectionExistsSolver,
    'not_exists': ConnectionNotExistsSolver
}

operator_to_complex_connection_solver_classes = {
    'and': AndConnectionSolver,
    'or': OrConnectionSolver
}

operator_to_filter_solver_classes = {
    'within': WithinFilterSolver,
}

condition_type_to_solver_type = {
    '': SolverType.ATTRIBUTE,
    'attribute': SolverType.ATTRIBUTE,
    'connection': SolverType.CONNECTION,
    'filter': SolverType.FILTER
}


class NXGraphCheckParser(BaseGraphCheckParser):
    def parse_raw_check(self, raw_check, **kwargs) -> BaseGraphCheck:
        policy_definition = raw_check.get("definition")
        check = self._parse_raw_check(policy_definition, kwargs.get("resources_types"))
        check.id = raw_check.get("metadata", {}).get("id")
        check.name = raw_check.get("metadata", {}).get("name")
        solver = self.get_check_solver(check)
        check.set_solver(solver)

        return check

    def _parse_raw_check(self, raw_check, resources_types):
        check = BaseGraphCheck()
        complex_operator = get_complex_operator(raw_check)
        if complex_operator:
            check.type = SolverType.COMPLEX
            check.operator = complex_operator
            sub_solvers = raw_check.get(complex_operator)
            for sub_solver in sub_solvers:
                check.sub_checks.append(self._parse_raw_check(sub_solver, resources_types))
            resources_types_of_sub_solvers = [q.resource_types for q in check.sub_checks
                                              if q is not None and q.resource_types is not None]
            check.resource_types = list(set(sum(resources_types_of_sub_solvers, [])))
            if any(q.type in [SolverType.CONNECTION, SolverType.COMPLEX_CONNECTION] for q in check.sub_checks):
                check.type = SolverType.COMPLEX_CONNECTION

        else:
            resource_type = raw_check.get("resource_types", [])
            if not resource_type or isinstance(resource_type, str) and resource_type.lower() == 'all' or\
                    isinstance(resource_type, list) and resource_type[0].lower() == 'all':
                check.resource_types = resources_types
            else:
                check.resource_types = resource_type

            connected_resources_type = raw_check.get('connected_resource_types', [])
            if connected_resources_type == ['All'] or connected_resources_type == 'all':
                check.connected_resources_types = resources_types
            else:
                check.connected_resources_types = connected_resources_type

            condition_type = raw_check.get('cond_type', '')
            check.type = condition_type_to_solver_type.get(condition_type)
            if condition_type == '':
                check.operator = 'any'
            else:
                check.operator = raw_check.get('operator')
            check.attribute = raw_check.get('attribute')
            check.attribute_value = raw_check.get('value')

        return check

    def get_check_solver(self, check):
        sub_solvers = []
        if check.sub_checks:
            sub_solvers = []
            for sub_solver in check.sub_checks:
                sub_solvers.append(self.get_check_solver(sub_solver))

        type_to_solver = {
            SolverType.COMPLEX_CONNECTION: operator_to_complex_connection_solver_classes.get(check.operator, lambda *args: None)(sub_solvers, check.operator),
            SolverType.COMPLEX: operators_to_complex_solver_classes.get(check.operator, lambda *args: None)(sub_solvers, check.resource_types),
            SolverType.ATTRIBUTE: operators_to_attributes_solver_classes.get(check.operator, lambda *args: None)(check.resource_types, check.attribute, check.attribute_value),
            SolverType.CONNECTION: operator_to_connection_solver_classes.get(check.operator, lambda *args: None)(check.resource_types, check.connected_resources_types),
            SolverType.FILTER: operator_to_filter_solver_classes.get(check.operator, lambda *args: None)(check.resource_types, check.attribute, check.attribute_value)
        }

        solver = type_to_solver.get(check.type)
        if not solver:
            raise NotImplementedError(f"solver type {check.type} with operator {check.operator} is not supported")
        return solver


def get_complex_operator(raw_check):
    for operator in operators_to_complex_solver_classes.keys():
        if raw_check.get(operator):
            return operator
    return None
