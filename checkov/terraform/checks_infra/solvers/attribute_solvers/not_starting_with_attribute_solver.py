from checkov.common.graph.checks_infra.enums import Operators
from .starting_with_attribute_solver import StartingWithAttributeSolver


class NotStartingWithAttributeSolver(StartingWithAttributeSolver):
    operator = Operators.NOT_STARTING_WITH

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return not super(NotStartingWithAttributeSolver, self)._get_operation(vertex, attribute)
