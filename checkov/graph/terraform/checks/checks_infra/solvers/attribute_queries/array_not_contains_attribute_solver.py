from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.array_contains_attribute_solver import ArrayContainsAttributeSolver


class ArrayNotContainsAttributeSolver(ArrayContainsAttributeSolver):
    operator = 'not_contains'

    def __init__(self, resource_types, query_attribute, query_value):
        super().__init__(resource_types=resource_types,
                         query_attribute=query_attribute, query_value=query_value)

    def _get_operation(self, *args):
        # TODO
        raise NotImplementedError
