from __future__ import annotations

import concurrent.futures
import re
from typing import List, Tuple, Dict, Any, Optional, Pattern, TYPE_CHECKING

from jsonpath_ng.ext import parse

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

from concurrent.futures import ThreadPoolExecutor

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.util.var_utils import is_terraform_variable_dependent
from checkov.terraform.graph_builder.graph_components.block_types import BlockType as TerraformBlockType

if TYPE_CHECKING:
    from networkx import DiGraph

SUPPORTED_BLOCK_TYPES = {BlockType.RESOURCE, TerraformBlockType.DATA, TerraformBlockType.MODULE}
WILDCARD_PATTERN = re.compile(r"(\S+[.][*][.]*)+")


class BaseAttributeSolver(BaseSolver):
    operator = ""  # noqa: CCE003  # a static attribute
    is_value_attribute_check = True    # noqa: CCE003  # a static attribute

    def __init__(
        self, resource_types: List[str], attribute: Optional[str], value: Any, is_jsonpath_check: bool = False
    ) -> None:
        super().__init__(SolverType.ATTRIBUTE)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value
        self.is_jsonpath_check = is_jsonpath_check
        self.parsed_attributes: Dict[Optional[str], Any] = {}

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        executer = ThreadPoolExecutor()
        jobs = []
        passed_vertices: List[Dict[str, Any]] = []
        failed_vertices: List[Dict[str, Any]] = []
        unknown_vertices: List[Dict[str, Any]] = []
        for _, data in graph_connector.nodes(data=True):
            if (not self.resource_types or data.get(CustomAttributes.RESOURCE_TYPE) in self.resource_types) \
                    and data.get(CustomAttributes.BLOCK_TYPE) in SUPPORTED_BLOCK_TYPES:
                jobs.append(executer.submit(
                    self._process_node, data, passed_vertices, failed_vertices, unknown_vertices))

        concurrent.futures.wait(jobs)
        return passed_vertices, failed_vertices, unknown_vertices

    def get_operation(self, vertex: Dict[str, Any]) -> Optional[bool]:
        attr_val = vertex.get(self.attribute)   # type:ignore[arg-type]  # due to attribute can be None
        # if this value contains an underendered variable, then we cannot evaluate value checks,
        # and will return None (for UNKNOWN)
        # handle edge cases in some policies that explicitly look for blank values
        if self.is_value_attribute_check and self._is_variable_dependant(attr_val, vertex['source_']) \
                and self.value != '':
            return None

        if self.attribute and (self.is_jsonpath_check or re.match(WILDCARD_PATTERN, self.attribute)):
            attribute_matches = self.get_attribute_matches(vertex)
            filtered_attribute_matches = attribute_matches
            if self.is_value_attribute_check and self.value != '':
                filtered_attribute_matches = [
                    a for a in attribute_matches
                    if not self._is_variable_dependant(vertex.get(a), vertex['source_'])
                ]

            if attribute_matches:
                if self.is_jsonpath_check:
                    if self.resource_type_pred(vertex, self.resource_types) and all(
                            self._get_operation(vertex=vertex, attribute=attr) for attr in filtered_attribute_matches):
                        return True if len(attribute_matches) == len(filtered_attribute_matches) else None
                    return False

                if self.resource_type_pred(vertex, self.resource_types) and any(
                        self._get_operation(vertex=vertex, attribute=attr) for attr in filtered_attribute_matches):
                    return True
                return False if len(attribute_matches) == len(filtered_attribute_matches) else None

        return self.resource_type_pred(vertex, self.resource_types) and self._get_operation(
            vertex=vertex, attribute=self.attribute
        )

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        raise NotImplementedError

    def _process_node(
        self, data: Dict[str, Any], passed_vartices: List[Dict[str, Any]], failed_vertices: List[Dict[str, Any]],
            unknown_vertices: List[Dict[str, Any]]
    ) -> None:
        if not self.resource_type_pred(data, self.resource_types):
            return
        result = self.get_operation(vertex=data)
        # A None indicate for UNKNOWN result - the vertex shouldn't be added to the passed or the failed vertices
        if result is None:
            unknown_vertices.append(data)
        elif result:
            passed_vartices.append(data)
        else:
            failed_vertices.append(data)

    def get_attribute_matches(self, vertex: Dict[str, Any]) -> List[str]:
        attribute_matches: List[str] = []
        if self.is_jsonpath_check:
            parsed_attr = self.parsed_attributes.get(self.attribute)
            if parsed_attr is None:
                parsed_attr = parse(self.attribute)
                self.parsed_attributes[self.attribute] = parsed_attr
            for match in parsed_attr.find(vertex):
                full_path = str(match.full_path)
                if full_path not in vertex:
                    vertex[full_path] = match.value

                attribute_matches.append(full_path)

        elif isinstance(self.attribute, str):
            attribute_patterns = self.get_attribute_patterns(self.attribute)
            for attr in vertex:
                if any(re.match(re.compile(attribute_pattern), attr) for attribute_pattern in attribute_patterns):
                    attribute_matches.append(attr)

        return attribute_matches

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

        pattern = f'^{"[.]".join(pattern_parts)}$'
        pattern_with_index = re.compile(pattern)

        pattern = f'^{"[.]".join(pattern_parts_without_index)}$'
        pattern_without_index = re.compile(pattern)

        return pattern_with_index, pattern_without_index

    @staticmethod
    def _is_variable_dependant(value: Any, source: str) -> bool:
        if source.lower() == 'terraform' and is_terraform_variable_dependent(value):
            return True
        # TODO add logic for CloudFormation
        # elif source == 'CloudFormation' and is_cloudformation_variable_dependent(value):
        #     return True

        return False
