import re

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

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
                                       self.resource_type_pred(data, self.resource_types)]
        passed_vertices = [data for data in all_vertices_resource_types if self.get_operation(vertex=data)]
        failed_vertices = [resource for resource in all_vertices_resource_types if resource not in passed_vertices]
        return passed_vertices, failed_vertices

    def get_operation(self, vertex):
        if re.match(WILDCARD_PATTERN, self.attribute):
            attribute_patterns = self.get_attribute_patterns(self.attribute)
            attribute_matches = [attr for attr in vertex if any(re.match(attribute_pattern, attr) for attribute_pattern in attribute_patterns)]
            if attribute_matches:
                return self.resource_type_pred(vertex, self.resource_types) and any(self._get_operation(vertex=vertex, attribute=attr) for attr in attribute_matches)
        return self.resource_type_pred(vertex, self.resource_types) and self._get_operation(vertex=vertex, attribute=self.attribute)

    def _get_operation(self, vertex, attribute):
        raise NotImplementedError

    @staticmethod
    def get_attribute_patterns(attribute):
        index_pattern = r"[\d+]"
        split_by_dots = attribute.split(".")
        pattern_parts = []
        for i, attr_part in enumerate(split_by_dots):
            if attr_part == "*":
                pattern_parts.append(index_pattern)
            else:
                pattern_parts.append(f"({attr_part})")
        pattern = "[.]".join(pattern_parts)
        pattern_with_index = re.compile(pattern)

        pattern_parts_without_index = []
        for pattern_part in pattern_parts:
            if pattern_part != index_pattern:
                pattern_parts_without_index.append(pattern_part)

        pattern = "[.]".join(pattern_parts_without_index)
        pattern_without_index = re.compile(pattern)

        return pattern_with_index, pattern_without_index
