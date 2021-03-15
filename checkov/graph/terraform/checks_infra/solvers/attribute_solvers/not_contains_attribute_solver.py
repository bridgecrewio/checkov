from .contains_attribute_solver import ContainsAttributeSolver


class NotContainsAttributeSolver(ContainsAttributeSolver):
    operator = 'not_contains'

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return not super(NotContainsAttributeSolver, self)._get_operation(vertex, attribute)
