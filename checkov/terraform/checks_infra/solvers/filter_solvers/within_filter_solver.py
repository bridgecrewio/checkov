from checkov.terraform.checks_infra.solvers.filter_solvers.base_filter_solver import BaseFilterSolver


class WithinFilterSolver(BaseFilterSolver):
    operator = 'within'

    def __init__(self, resource_types, query_attribute, query_value):
        super().__init__(resource_types=resource_types,
                         query_attribute=query_attribute, query_value=query_value)

    def get_operation(self, *args, **kwargs):
        return self._get_operation()(*args)

    def _get_operation(self, *args, **kwargs):
        return lambda check: check.get(self.query_attribute) in self.query_value
