import re

from checkov.graph.checks.checks_infra.enums import SolverType
from checkov.graph.checks.checks_infra.solvers.base_solver import BaseSolver

WILDCARD_PATTERN = re.compile(r"(\S+[.][*][.]*)+")


class BaseAttributeSolver(BaseSolver):
    operator = ''

    def __init__(self, resource_types, attribute, value):
        super().__init__(SolverType.ATTRIBUTE)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value

    def run(self, graph_connector):
        all_vertices_resource_types = [data for _, data in graph_connector.nodes(data=True) if
                                       self.resource_type_pred(data)]
        passed_vertices = [data for data in all_vertices_resource_types if self.get_operation(vertex=data)]
        failed_vertices = [resource for resource in all_vertices_resource_types if resource not in passed_vertices]
        return passed_vertices, failed_vertices

    def get_operation(self, vertex):
        if not re.match(WILDCARD_PATTERN, self.attribute):
            return self.resource_type_pred(vertex) and self._get_operation(vertex=vertex, attribute=self.attribute)
        attribute_pattern = self.get_attribute_pattern(self.attribute)
        return self.resource_type_pred(vertex) and any(self._get_operation(vertex=vertex, attribute=attr) for attr in vertex if re.match(attribute_pattern, attr))

    def _get_operation(self, vertex, attribute):
        raise NotImplementedError

    def resource_type_pred(self, v):
        return len(self.resource_types) == 0 or v.get('resource_type') in self.resource_types

    @staticmethod
    def get_attribute_pattern(attribute):
        split_by_dots = attribute.split(".")
        pattern_parts = []
        for i, attr_part in enumerate(split_by_dots):
            if attr_part == "*":
                pattern_parts.append(r"[\d+]")
            else:
                pattern_parts.append(f"({attr_part})")
        pattern = "[.]".join(pattern_parts)
        p = re.compile(pattern)
        return p
