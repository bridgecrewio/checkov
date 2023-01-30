from __future__ import annotations

import logging
import os
import platform

from typing import Type, Optional

from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.output.record import Record
from checkov.common.util.secrets import omit_secret_value_from_checks

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import CHECKOV_CREATE_GRAPH
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.plan_utils import create_definitions, build_definitions_context, \
    get_resource_id_without_nested_modules
from checkov.terraform.runner import Runner as TerraformRunner, merge_reports
from checkov.terraform.deep_analysis_plan_graph_manager import DeepAnalysisGraphManager


# set of check IDs with lifecycle condition
TF_LIFECYCLE_CHECK_IDS = {
    "CKV_AWS_217",
    "CKV_AWS_233",
    "CKV_AWS_237",
    "CKV_GCP_82",
}

RESOURCE_ATTRIBUTES_TO_OMIT = {
    'aws_db_instance': ['password'],
    'aws_secretsmanager_secret_version': ['secret_string'],
    'aws_ssm_parameter': ['value'],
    'azurerm_container_registry': ['admin_password'],
    'azurerm_key_vault_secret': ['value'],
    'azurerm_linux_virtual_machine': ['admin_password'],
    'azurerm_mssql_managed_instance_vulnerability_assessment': ['storage_container_path'],
    'azurerm_mssql_server': ['administrator_login_password'],
    'azurerm_mssql_server_vulnerability_assessment': ['storage_container_path'],
    'azurerm_redis_cache': ['primary_access_key', 'secondary_access_key', 'primary_connection_string',
                            'secondary_connection_string'],
    'azurerm_sql_server': ['administrator_login_password'],
    'azurerm_sql_managed_instance': ['administrator_login_password'],
    'azurerm_storage_account': ['primary_access_key', 'secondary_access_key', 'primary_blob_connection_string',
                                'secondary_blob_connection_string', 'primary_blob_endpoint', 'primary_blob_host',
                                'secondary_blob_endpoint', 'secondary_blob_host', 'primary_connection_string',
                                'secondary_connection_string'],
    'azurerm_synapse_workspace_vulnerability_assessment': ['storage_container_path'],
    'azurerm_synapse_sql_pool_vulnerability_assessment': ['storage_container_path'],
    'azurerm_virtual_machine': ['admin_password'],
    'azurerm_windows_virtual_machine': ['admin_password'],
    'google_kms_secret_ciphertext': ['plaintext']
}


class Runner(TerraformRunner):
    check_type = CheckType.TERRAFORM_PLAN  # noqa: CCE003  # a static attribute

    def __init__(self, graph_class: Type[TerraformLocalGraph] = TerraformLocalGraph,
                 graph_manager: TerraformGraphManager | None = None,
                 db_connector: LibraryGraphConnector | None = None,
                 external_registries: list[BaseRegistry] | None = None,
                 source: str = GraphSource.TERRAFORM) -> None:
        super().__init__(
            graph_class=graph_class,
            graph_manager=graph_manager,
            db_connector=db_connector,
            external_registries=external_registries,
            source=source,
        )
        self.file_extensions = ['.json']  # override what gets set from the TF runner
        self.definitions = None
        self.context = None
        self.graph_registry = get_graph_checks_registry(super().check_type)
        self.deep_analysis = False
        self.repo_root_for_plan_enrichment = []
        self.tf_plan_local_graph = None

    block_type_registries = {  # noqa: CCE003  # a static attribute
        'resource': resource_registry,
    }

    def run(
            self,
            root_folder: str | None = None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        # Update resource_attr_to_omit according to plan runner hardcoded RESOURCE_ATTRIBUTES_TO_OMIT
        self._extend_resource_attributes_to_omit(runner_filter)
        self.deep_analysis = runner_filter.deep_analysis
        if runner_filter.repo_root_for_plan_enrichment:
            self.repo_root_for_plan_enrichment = os.path.abspath(runner_filter.repo_root_for_plan_enrichment[0])
        report = Report(self.check_type)
        parsing_errors: dict[str, str] = {}
        tf_local_graph: Optional[TerraformLocalGraph] = None
        if self.definitions is None or self.context is None:
            self.definitions, definitions_raw = create_definitions(root_folder, files, runner_filter, parsing_errors)
            self.context = build_definitions_context(self.definitions, definitions_raw)
            if CHECKOV_CREATE_GRAPH:
                self.tf_plan_local_graph = self.graph_manager.build_graph_from_definitions(self.definitions, render_variables=False)
                for vertex in self.tf_plan_local_graph.vertices:
                    if vertex.block_type == BlockType.RESOURCE:
                        address = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS)
                        if self.enable_nested_modules:
                            report.add_resource(f'{vertex.path}:{address}')
                        else:
                            resource_id = get_resource_id_without_nested_modules(address)
                            report.add_resource(f'{vertex.path}:{resource_id}')
                self.graph_manager.save_graph(self.tf_plan_local_graph)
                if self._should_run_deep_analysis:
                    tf_local_graph = self._create_terraform_graph()

        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)
        if not root_folder:
            root_folder = os.path.split(os.path.commonprefix(files))[0]
        self.check_tf_definition(report, root_folder, runner_filter)
        report.add_parsing_errors(parsing_errors.keys())

        if self.definitions:
            graph_report = self._get_graph_report(
                root_folder=root_folder,
                runner_filter=runner_filter,
                tf_local_graph=tf_local_graph
            )
            merge_reports(report, graph_report)

        if runner_filter.run_image_referencer:
            image_report = self.check_container_image_references(
                graph_connector=self.graph_manager.get_reader_endpoint(),
                root_path=root_folder,
                runner_filter=runner_filter,
            )

            if image_report:
                # due too many tests failing only return a list, if there is an image report
                return [report, image_report]

        return report

    @staticmethod
    def _extend_resource_attributes_to_omit(runner_filter: RunnerFilter):
        for k, v in RESOURCE_ATTRIBUTES_TO_OMIT.items():
            # It's ok as runner_filter is ALWAYS default dict with set() as value
            runner_filter.resource_attr_to_omit[k].update(v)

    def _get_graph_report(
            self,
            root_folder: str,
            runner_filter: RunnerFilter,
            tf_local_graph: Optional[TerraformLocalGraph]
    ) -> Report:
        if self._should_run_deep_analysis and tf_local_graph:
            deep_analysis_graph_manager = DeepAnalysisGraphManager(tf_local_graph, self.tf_plan_local_graph)
            deep_analysis_graph_manager.enrich_tf_graph_attributes()
            self.graph_manager.save_graph(tf_local_graph)
            graph_report = self.get_graph_checks_report(root_folder, runner_filter)
            deep_analysis_graph_manager.filter_report(graph_report)
            return graph_report
        return self.get_graph_checks_report(root_folder, runner_filter)

    def _create_terraform_graph(self) -> TerraformLocalGraph:
        graph_manager = TerraformGraphManager(db_connector=self.db_connector)
        tf_local_graph, _ = graph_manager.build_graph_from_source_directory(
            self.repo_root_for_plan_enrichment,
            render_variables=True
        )
        self.graph_manager = graph_manager
        return tf_local_graph

    def check_tf_definition(self, report, root_folder, runner_filter, collect_skip_comments=True):
        for full_file_path, definition in self.definitions.items():
            if platform.system() == "Windows":
                temp = os.path.split(full_file_path)[0]
                scanned_file = f"/{os.path.relpath(full_file_path,temp)}"
            else:
                scanned_file = f"/{os.path.relpath(full_file_path, root_folder)}"
            logging.debug(f"Scanning file: {scanned_file}")
            for block_type in definition.keys():
                if block_type in self.block_type_registries.keys():
                    self.run_block(definition[block_type], None, full_file_path, root_folder, report, scanned_file,
                                   block_type, runner_filter)

    def run_block(self, entities,
                  definition_context,
                  full_file_path, root_folder, report, scanned_file,
                  block_type, runner_filter=None, entity_context_path_header=None,
                  module_referrer: str | None = None):
        registry = self.block_type_registries[block_type]
        if registry:
            for entity in entities:
                context_parser = parser_registry.context_parsers[block_type]
                definition_path = context_parser.get_entity_context_path(entity)
                # Entity can exist only once per dir, for file as well
                entity_context = self.get_entity_context(definition_path, full_file_path)
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                entity_address = entity_context.get('address')
                entity_id = entity_address if self.enable_nested_modules else get_resource_id_without_nested_modules(entity_address)
                _, _, entity_config = registry.extract_entity_details(entity)

                results = registry.scan(scanned_file, entity, [], runner_filter, report_type=CheckType.TERRAFORM_PLAN)
                for check, check_result in results.items():
                    if check.id in TF_LIFECYCLE_CHECK_IDS:
                        # can't be evaluated in TF plan
                        continue
                    censored_code_lines = omit_secret_value_from_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_code_lines,
                        entity_config=entity_config,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                    )
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=check_result,
                        code_block=censored_code_lines,
                        file_path=scanned_file,
                        file_line_range=entity_lines_range,
                        resource=entity_id,
                        resource_address=entity_address,
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=full_file_path,
                        severity=check.severity,
                        details=check.details,
                    )
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)

    def get_entity_context_and_evaluations(self, entity):
        raw_context = self.get_entity_context(entity[CustomAttributes.BLOCK_NAME].split("."),
                                              entity[CustomAttributes.FILE_PATH])
        if raw_context:
            raw_context['definition_path'] = entity[CustomAttributes.BLOCK_NAME].split('.')
        return raw_context, None

    def get_entity_context(self, definition_path, full_file_path):
        entity_id = ".".join(definition_path)
        return self.context.get(full_file_path, {}).get(entity_id)

    @property
    def _should_run_deep_analysis(self) -> bool:
        return self.deep_analysis and self.repo_root_for_plan_enrichment and self.tf_plan_local_graph
