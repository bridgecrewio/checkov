from .ending_with_attribute_solver import EndingWithAttributeSolver


class NotEndingWithAttributeSolver(EndingWithAttributeSolver):
    operator = 'not_ending_with'

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return not super(NotEndingWithAttributeSolver, self)._get_operation(vertex, attribute)
