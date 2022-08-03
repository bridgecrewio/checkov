import logging
import os
import platform

from typing import Optional, List, Type

from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import CHECKOV_CREATE_GRAPH
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.plan_utils import create_definitions, build_definitions_context
from checkov.terraform.runner import Runner as TerraformRunner, merge_reports

# set of check IDs with lifecycle condition
TF_LIFECYCLE_CHECK_IDS = {
    "CKV_AWS_217",
    "CKV_AWS_233",
    "CKV_AWS_237",
    "CKV_GCP_82",
}


class Runner(TerraformRunner):
    check_type = CheckType.TERRAFORM_PLAN

    def __init__(self, graph_class: Type[LocalGraph] = TerraformLocalGraph,
                 graph_manager: Optional[TerraformGraphManager] = None,
                 db_connector: NetworkxConnector = NetworkxConnector(),
                 external_registries: Optional[List[BaseRegistry]] = None,
                 source: str = "Terraform"):
        super().__init__(graph_class=graph_class, graph_manager=graph_manager, db_connector=db_connector,
                         external_registries=external_registries, source=source)
        self.file_extensions = ['.json']  # override what gets set from the TF runner
        self.definitions = None
        self.context = None
        self.graph_registry = get_graph_checks_registry(super().check_type)

    block_type_registries = {
        'resource': resource_registry,
    }

    def run(
            self,
            root_folder: Optional[str] = None,
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: RunnerFilter = RunnerFilter(),
            collect_skip_comments: bool = True
    ) -> Report:
        report = Report(self.check_type)
        parsing_errors = {}
        if self.definitions is None or self.context is None:
            self.definitions, definitions_raw = create_definitions(root_folder, files, runner_filter, parsing_errors)
            self.context = build_definitions_context(self.definitions, definitions_raw)
            if CHECKOV_CREATE_GRAPH:
                graph = self.graph_manager.build_graph_from_definitions(self.definitions, render_variables=False)
                self.graph_manager.save_graph(graph)

        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)
        self.check_tf_definition(report, root_folder, runner_filter)
        report.add_parsing_errors(parsing_errors.keys())

        if self.definitions:
            graph_report = self.get_graph_checks_report(root_folder, runner_filter)
            merge_reports(report, graph_report)
        return report

    def check_tf_definition(self, report, root_folder, runner_filter, collect_skip_comments=True):
        for full_file_path, definition in self.definitions.items():
            if platform.system() == "Windows":
                temp = os.path.split(full_file_path)[0]
                scanned_file = f"/{os.path.relpath(full_file_path,temp)}"
            else:
                scanned_file = f"/{os.path.relpath(full_file_path)}"
            logging.debug(f"Scanning file: {scanned_file}")
            for block_type in definition.keys():
                if block_type in self.block_type_registries.keys():
                    self.run_block(definition[block_type], None, full_file_path, root_folder, report, scanned_file,
                                   block_type, runner_filter)

    def run_block(self, entities,
                  definition_context,
                  full_file_path, root_folder, report, scanned_file,
                  block_type, runner_filter=None, entity_context_path_header=None,
                  module_referrer: Optional[str] = None):
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)
                entity_id = ".".join(definition_path)
                # Entity can exist only once per dir, for file as well
                entity_context = self.get_entity_context(definition_path, full_file_path)
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                entity_address = entity_context.get('address')

                results = registry.scan(scanned_file, entity, [], runner_filter)
                for check, check_result in results.items():
                    if check.id in TF_LIFECYCLE_CHECK_IDS:
                        # can't be evaluated in TF plan
                        continue

                    record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                                    check_result=check_result,
                                    code_block=entity_code_lines, file_path=scanned_file,
                                    file_line_range=entity_lines_range,
                                    resource=entity_id, resource_address=entity_address, evaluations=None,
                                    check_class=check.__class__.__module__, file_abs_path=full_file_path,
                                    severity=check.severity)
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)

    def get_entity_context_and_evaluations(self, entity):
        raw_context = self.get_entity_context(entity[CustomAttributes.BLOCK_NAME].split("."),
                                              entity[CustomAttributes.FILE_PATH])
        raw_context['definition_path'] = entity[CustomAttributes.BLOCK_NAME].split('.')
        return raw_context, None

    def get_entity_context(self, definition_path, full_file_path):
        entity_id = ".".join(definition_path)
        return self.context.get(full_file_path, {}).get(entity_id)
