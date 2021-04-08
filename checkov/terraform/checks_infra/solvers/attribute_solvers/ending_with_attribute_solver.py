from checkov.common.graph.checks_infra.enums import Operators
from checkov.terraform.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class EndingWithAttributeSolver(BaseAttributeSolver):
    operator = Operators.CONTAINS

    def __init__(self, resource_types, attribute, value):
        super().__init__(resource_types=resource_types,
                         attribute=attribute, value=value)

    def _get_operation(self, vertex, attribute):
        return isinstance(vertex.get(attribute), str) and vertex.get(attribute).endswith(self.value)
