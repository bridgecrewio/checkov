import logging

from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.common.output.report import Report
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_ADDRESS
from typing import Dict


class DeepAnalysisGraphManager:
    def __init__(self, tf_graph: TerraformLocalGraph, tf_plan_graph: TerraformLocalGraph) -> None:
        self.tf_graph: TerraformLocalGraph = tf_graph
        self.tf_plan_graph: TerraformLocalGraph = tf_plan_graph
        self._address_to_tf_vertex_map: Dict[str, TerraformBlock] = {}
        self._address_to_tf_plan_vertex_map: Dict[str, TerraformBlock] = {}
        self._apply_address_mapping()

    def _apply_address_mapping(self) -> None:
        self._address_to_tf_vertex_map = {
            vertex.attributes[TF_PLAN_RESOURCE_ADDRESS]: vertex
            for vertex in self.tf_graph.vertices
            if vertex.block_type == BlockType.RESOURCE
        }
        self._address_to_tf_plan_vertex_map = {
            vertex.attributes[TF_PLAN_RESOURCE_ADDRESS]: vertex
            for vertex in self.tf_plan_graph.vertices
            if vertex.block_type == BlockType.RESOURCE
        }

    def enrich_tf_graph_attributes(self) -> None:
        for address, tf_plan_vertex in self._address_to_tf_plan_vertex_map.items():
            tf_vertex = self._address_to_tf_vertex_map.get(address)
            if not tf_vertex:
                logging.info(f'Cant find this address: {address} in tf graph')
                continue
            tf_vertex.attributes = {**tf_vertex.attributes, **tf_plan_vertex.attributes}
            tf_vertex.path = tf_plan_vertex.path

    def filter_report(self, report: Report) -> None:
        report.failed_checks = [check for check in report.failed_checks if
                                check.resource_address in self._address_to_tf_plan_vertex_map]
        report.passed_checks = [check for check in report.passed_checks if
                                check.resource_address in self._address_to_tf_plan_vertex_map]
        report.skipped_checks = [check for check in report.skipped_checks if
                                 check.resource_address in self._address_to_tf_plan_vertex_map]
        # No need to filter other fields for now
        report.resources = set()
        report.extra_resources = set()
        report.parsing_errors = []
