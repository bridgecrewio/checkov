import logging

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.common.output.report import Report
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_ADDRESS
from typing import Dict, Tuple, Optional


class DeepAnalysisGraphManager:
    def __init__(self, tf_graph: TerraformLocalGraph, tf_plan_graph: TerraformLocalGraph) -> None:
        self.tf_graph: TerraformLocalGraph = tf_graph
        self.tf_plan_graph: TerraformLocalGraph = tf_plan_graph
        self._address_to_tf_idx_and_vertex_map: Dict[str, Tuple[int, TerraformBlock]] = {}
        self._address_to_tf_plan_idx_and_vertex_map: Dict[str, Tuple[int, TerraformBlock]] = {}
        self._apply_address_mapping()

    def _apply_address_mapping(self) -> None:
        self._address_to_tf_idx_and_vertex_map = {
            vertex.attributes[TF_PLAN_RESOURCE_ADDRESS]: (i, vertex)
            for i, vertex in enumerate(self.tf_graph.vertices)
            if vertex.block_type == BlockType.RESOURCE
        }
        self._address_to_tf_plan_idx_and_vertex_map = {
            vertex.attributes[TF_PLAN_RESOURCE_ADDRESS]: (i, vertex)
            for i, vertex in enumerate(self.tf_plan_graph.vertices)
            if vertex.block_type == BlockType.RESOURCE
        }

    def _get_tf_vertex_idx_from_tf_plan_vertex(self, v: TerraformBlock) -> Optional[int]:
        vertex = self._address_to_tf_idx_and_vertex_map.get(v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS, ''))
        if vertex is None:
            return None
        return vertex[0]

    def append_vertex_to_terraform_graph(self, tf_plan_vertex: TerraformBlock, tf_plan_vertex_index: int, address: str) -> None:
        new_vertex_idx = len(self.tf_graph.vertices)
        self.tf_graph.vertices.append(tf_plan_vertex)
        self._address_to_tf_idx_and_vertex_map[address] = (new_vertex_idx, tf_plan_vertex)

        for edge in self.tf_plan_graph.out_edges[tf_plan_vertex_index]:
            dest = self.tf_plan_graph.vertices[edge.dest]
            dest_index = self._get_tf_vertex_idx_from_tf_plan_vertex(dest)
            if dest_index:
                self.tf_graph.create_edge(new_vertex_idx, dest_index, edge.label)
        for edge in self.tf_plan_graph.in_edges[tf_plan_vertex_index]:
            origin = self.tf_plan_graph.vertices[edge.origin]
            origin_index = self._get_tf_vertex_idx_from_tf_plan_vertex(origin)
            if origin_index:
                self.tf_graph.create_edge(origin_index, new_vertex_idx, edge.label)

    def enrich_tf_graph_attributes(self) -> None:
        for address, tf_plan_idx_and_vertex in self._address_to_tf_plan_idx_and_vertex_map.items():
            tf_plan_vertex_index, tf_plan_vertex = tf_plan_idx_and_vertex
            tf_idx_and_vertex = self._address_to_tf_idx_and_vertex_map.get(address)
            if not tf_idx_and_vertex:
                logging.info(f'Cant find this address: {address} in tf graph, adding it')
                self.append_vertex_to_terraform_graph(tf_plan_vertex, tf_plan_vertex_index, address)
                continue
            _, tf_vertex = tf_idx_and_vertex
            tf_vertex.attributes = {**tf_vertex.attributes, **tf_plan_vertex.attributes}
            tf_vertex.path = tf_plan_vertex.path

    def filter_report(self, report: Report) -> None:
        report.failed_checks = [check for check in report.failed_checks if
                                check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        report.passed_checks = [check for check in report.passed_checks if
                                check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        report.skipped_checks = [check for check in report.skipped_checks if
                                 check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        # No need to filter other fields for now
        report.resources = set()
        report.extra_resources = set()
        report.parsing_errors = []
