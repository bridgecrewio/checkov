from __future__ import annotations

import concurrent.futures
import logging
import re
import json
from typing import List, Tuple, Dict, Any, Optional, Pattern, TYPE_CHECKING

from bc_jsonpath_ng.ext import parse
from networkx import DiGraph

from checkov.common.graph.checks_infra import debug
from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

from concurrent.futures import ThreadPoolExecutor

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.util.var_utils import is_terraform_variable_dependent
from checkov.terraform.graph_builder.graph_components.block_types import BlockType as TerraformBlockType

if TYPE_CHECKING:
    from bc_jsonpath_ng import JSONPath
    from checkov.common.typing import LibraryGraph

SUPPORTED_BLOCK_TYPES = {BlockType.RESOURCE, TerraformBlockType.DATA, TerraformBlockType.MODULE, TerraformBlockType.PROVIDER}
WILDCARD_PATTERN = re.compile(r"(\S+[.][*][.]*)+")


class BaseAttributeSolver(BaseSolver):
    operator = ""  # noqa: CCE003  # a static attribute
    is_value_attribute_check = True  # noqa: CCE003  # a static attribute
    jsonpath_parsed_statement_cache: "dict[str, JSONPath]" = {}  # noqa: CCE003  # global cache

    def __init__(
        self, resource_types: List[str], attribute: Optional[str], value: Any, is_jsonpath_check: bool = False
    ) -> None:
        super().__init__(SolverType.ATTRIBUTE)
        self.resource_types = resource_types
        self.attribute = attribute
        self.value = value
        self.is_jsonpath_check = is_jsonpath_check

    def run(self, graph_connector: LibraryGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        executer = ThreadPoolExecutor()
        jobs = []
        passed_vertices: List[Dict[str, Any]] = []
        failed_vertices: List[Dict[str, Any]] = []
        unknown_vertices: List[Dict[str, Any]] = []

        if isinstance(graph_connector, DiGraph):
            for _, data in graph_connector.nodes(data=True):
                if (not self.resource_types or data.get(CustomAttributes.RESOURCE_TYPE) in self.resource_types) \
                        and data.get(CustomAttributes.BLOCK_TYPE) in SUPPORTED_BLOCK_TYPES:
                    jobs.append(executer.submit(
                        self._process_node, data, passed_vertices, failed_vertices, unknown_vertices))

            concurrent.futures.wait(jobs)
            return passed_vertices, failed_vertices, unknown_vertices

        for _, data in graph_connector.nodes():
            if (not self.resource_types or data.get(CustomAttributes.RESOURCE_TYPE) in self.resource_types) \
                    and data.get(CustomAttributes.BLOCK_TYPE) in SUPPORTED_BLOCK_TYPES:
                jobs.append(executer.submit(
                    self._process_node, data, passed_vertices, failed_vertices, unknown_vertices))

        concurrent.futures.wait(jobs)
        return passed_vertices, failed_vertices, unknown_vertices

    def get_operation(self, vertex: Dict[str, Any]) -> Optional[bool]:
        # if this value contains an underendered variable, then we cannot evaluate value checks,
        # and will return None (for UNKNOWN)
        # handle edge cases in some policies that explicitly look for blank values
        # we also need to check the attribute stack - e.g., if they are looking for tags.component, but tags = local.tags,
        # then we actually need to see if tags is variable dependent as well
        attr_parts = self.attribute.split('.')  # type:ignore[union-attr]  # due to attribute can be None (but not really)
        attr_to_check = None
        for attr in attr_parts:
            attr_to_check = f'{attr_to_check}.{attr}' if attr_to_check else attr
            value_to_check = vertex.get(attr_to_check)
            value_to_check = self._render_json_str(value_to_check, attr, vertex)

            # we can only check is_attribute_value_check when evaluating the full attribute
            # for example, if we have a policy that says "tags.component exists", and tags = local.tags, then
            # we need to check if tags is variable dependent even though this is a not value_attribute check
            if (attr_to_check != self.attribute or self.is_value_attribute_check) \
                    and self._is_variable_dependant(value_to_check, vertex['source_']) \
                    and self.value != '':
                return None

        if self.attribute and (self.is_jsonpath_check or re.match(WILDCARD_PATTERN, self.attribute)):
            attribute_matches = self.get_attribute_matches(vertex)
            filtered_attribute_matches = attribute_matches
            if self.is_value_attribute_check and self.value != '':
                filtered_attribute_matches = []
                for attribute in attribute_matches:
                    resource_variable_dependant = self._is_variable_dependant(vertex.get(attribute), vertex['source_'])
                    policy_variable_dependant = self._is_variable_dependant(self.value, vertex['source_'])
                    if not resource_variable_dependant or resource_variable_dependant and policy_variable_dependant:
                        filtered_attribute_matches.append(attribute)
            if attribute_matches:
                result = self._evaluate_attribute_matches(
                    vertex=vertex,
                    attribute_matches=attribute_matches,
                    filtered_attribute_matches=filtered_attribute_matches,
                )
                if result is not None:
                    # skip unknown
                    debug.attribute_block(
                        resource_types=self.resource_types,
                        attribute=self.attribute,
                        operator=self.operator,
                        value=self.value,
                        resource=vertex,
                        status="passed" if result is True else "failed",
                    )

                return result

        result = self.resource_type_pred(vertex, self.resource_types) and self._get_operation(
            vertex=vertex, attribute=self.attribute
        )

        debug.attribute_block(
            resource_types=self.resource_types,
            attribute=self.attribute,
            operator=self.operator,
            value=self.value,
            resource=vertex,
            status="passed" if result is True else "failed",
        )

        return result

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

    def _evaluate_attribute_matches(
        self, vertex: dict[str, Any], attribute_matches: list[str], filtered_attribute_matches: list[str]
    ) -> bool | None:
        if self.is_jsonpath_check:
            if self.resource_type_pred(vertex, self.resource_types) and all(
                self._get_operation(vertex=vertex, attribute=attr) for attr in filtered_attribute_matches
            ):
                return True if len(attribute_matches) == len(filtered_attribute_matches) else None
            return False

        if self.resource_type_pred(vertex, self.resource_types) and any(
            self._get_operation(vertex=vertex, attribute=attr) for attr in filtered_attribute_matches
        ):
            return True
        return False if len(attribute_matches) == len(filtered_attribute_matches) else None

    def get_attribute_matches(self, vertex: Dict[str, Any]) -> List[str]:
        try:
            attribute_matches: List[str] = []
            if self.is_jsonpath_check and self.attribute:
                parsed_attr = self._get_cached_jsonpath_statement(statement=self.attribute)

                for match in parsed_attr.find(vertex):
                    full_path = str(match.full_path)
                    if full_path not in vertex:
                        vertex[full_path] = match.value

                    attribute_matches.append(full_path)
            elif isinstance(self.attribute, str):
                attribute_patterns = self.get_attribute_patterns(self.attribute)
                attribute_parts = [attr for attr in self.attribute.split(".") if attr != "*"]
                for attr in vertex:
                    if any(part not in attr for part in attribute_parts):
                        # if even one attribute part doesn't exist in the vertex attribute, then no need to further proceed
                        continue
                    if any(re.match(attribute_pattern, attr) for attribute_pattern in attribute_patterns):
                        attribute_matches.append(attr)

            return attribute_matches
        except Exception:
            logging.debug('Error parsing or evaluating jsonpath expression', exc_info=True)
            raise

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

    @staticmethod
    def _render_json_str(value_to_check: Any, attr: str, vertex: Dict[str, Any]) -> Any:
        if attr == 'policy' and vertex.get('resource_type', '').endswith('policy'):
            if isinstance(value_to_check, dict):
                # it was already properly loaded
                return value_to_check

            try:
                value_to_check = json.loads(value_to_check)
                return value_to_check
            except Exception as e:
                logging.info(f'cant parse policy str to object, {str(e)}')
        return value_to_check

    def _get_cached_jsonpath_statement(self, statement: str) -> JSONPath:
        """Returns the parsed jsonpath statement from the cache or adds it"""

        if statement not in BaseAttributeSolver.jsonpath_parsed_statement_cache:
            parsed_attr = parse(statement)
            BaseAttributeSolver.jsonpath_parsed_statement_cache[statement] = parsed_attr
            return parsed_attr

        return BaseAttributeSolver.jsonpath_parsed_statement_cache[statement]
