from checkov.graph.terraform.checks.checks_infra.solvers.attribute_queries.base_attribute_solver import BaseAttributeSolver


class NotEndingWithAttributeSolver(BaseAttributeSolver):
    operator = 'not_ending_with'

    def __init__(self, resource_types, query_attribute, query_value):
        super().__init__(resource_types=resource_types,
                         query_attribute=query_attribute, query_value=query_value)

    def _get_operation(self):
        # TODO
        raise NotImplementedError
