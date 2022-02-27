import concurrent.futures
import re
from typing import List, Tuple, Dict, Any, Optional, Pattern

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

from concurrent.futures import ThreadPoolExecutor

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType

WILDCARD_PATTERN = re.compile(r"(\S+[.][*][.]*)+")


class BaseAttributeSolver(BaseSolver):
    operator = ""

    def __init__(self, resource_types: List[str], attribute: Optional[str], value: Any) -> None:
        super().__init__(SolverType.ATTRIBUTE)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        executer = ThreadPoolExecutor()
        jobs = []
        passed_vertices: List[Dict[str, Any]] = []
        failed_vertices: List[Dict[str, Any]] = []
        for _, data in graph_connector.nodes(data=True):
            if (not self.resource_types or data.get(CustomAttributes.RESOURCE_TYPE) in self.resource_types) \
                    and data.get(CustomAttributes.BLOCK_TYPE) == BlockType.RESOURCE:
                jobs.append(executer.submit(self._process_node, data, passed_vertices, failed_vertices))

        concurrent.futures.wait(jobs)
        return passed_vertices, failed_vertices

    def get_operation(self, vertex: Dict[str, Any]) -> bool:
        if self.attribute and re.match(WILDCARD_PATTERN, self.attribute):
            attribute_patterns = self.get_attribute_patterns(self.attribute)
            attribute_matches = [
                attr
                for attr in vertex
                if any(re.match(re.compile(attribute_pattern), attr) for attribute_pattern in attribute_patterns)
            ]
            if attribute_matches:
                return self.resource_type_pred(vertex, self.resource_types) and any(
                    self._get_operation(vertex=vertex, attribute=attr) for attr in attribute_matches
                )
        return self.resource_type_pred(vertex, self.resource_types) and self._get_operation(
            vertex=vertex, attribute=self.attribute
        )

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        raise NotImplementedError

    def _process_node(
        self, data: Dict[str, Any], passed_vartices: List[Dict[str, Any]], failed_vertices: List[Dict[str, Any]]
    ) -> None:
        if not self.resource_type_pred(data, self.resource_types):
            return
        if self.get_operation(vertex=data):
            passed_vartices.append(data)
        else:
            failed_vertices.append(data)

    @staticmethod
    def get_attribute_patterns(attribute: str) -> Tuple[Pattern[str], Pattern[str]]:
        index_pattern = r"[\d]+"
        split_by_dots = attribute.split(".")

        pattern_parts = []
        pattern_parts_without_index = []
        for attr_part in split_by_dots:
            if attr_part == "*":
                pattern_parts.append(index_pattern)
            else:
                attr_part_pattern = f"({attr_part})"
                pattern_parts.append(attr_part_pattern)
                pattern_parts_without_index.append(attr_part_pattern)

        pattern = "[.]".join(pattern_parts)
        pattern_with_index = re.compile(pattern)

        pattern = "[.]".join(pattern_parts_without_index)
        pattern_without_index = re.compile(pattern)

        return pattern_with_index, pattern_without_index
