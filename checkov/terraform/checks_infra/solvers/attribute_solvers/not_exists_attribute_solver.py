from checkov.common.graph.checks_infra.enums import Operators
from .exists_attribute_solver import ExistsAttributeSolver


class NotExistsAttributeSolver(ExistsAttributeSolver):
    operator = Operators.NOT_EXISTS

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return not super(NotExistsAttributeSolver, self)._get_operation(vertex, attribute)
