from checkov.common.graph.checks_infra.enums import Operators
from .equals_attribute_solver import EqualsAttributeSolver


class NotEqualsAttributeSolver(EqualsAttributeSolver):
    operator = Operators.NOT_EQUALS

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return not super(NotEqualsAttributeSolver, self)._get_operation(vertex, attribute)
