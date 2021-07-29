import copy
import dataclasses
import logging
import os
from typing import Dict, Optional, Tuple, List

import dpath.util

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.models.enums import CheckResult
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, remove_duplicate_results
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.util import data_structures_utils
from checkov.common.variables.context import EvaluationContext
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_manager import TerraformGraphManager
# Allow the evaluation of empty variables
from checkov.terraform.parser import Parser
from checkov.terraform.tag_providers import get_resource_tags

dpath.options.ALLOW_EMPTY_STRING_KEYS = True

CHECK_BLOCK_TYPES = frozenset(['resource', 'data', 'provider', 'module'])


class Runner(BaseRunner):
    check_type = "terraform"

    def __init__(self, parser=Parser(), db_connector=NetworkxConnector(), external_registries=None,
                 source="Terraform", graph_class=TerraformLocalGraph, graph_manager=None):
        self.external_registries = [] if external_registries is None else external_registries
        self.graph_class = graph_class
        self.parser = parser
        self.definitions = None
        self.context = None
        self.breadcrumbs = None
        self.evaluations_context: Dict[str, Dict[str, EvaluationContext]] = {}
        self.graph_manager = graph_manager if graph_manager is not None else TerraformGraphManager(source=source,
                                                                                                   db_connector=db_connector)
        self.graph_registry = get_graph_checks_registry(self.check_type)

    block_type_registries = {
        'resource': resource_registry,
        'data': data_registry,
        'provider': provider_registry,
        'module': module_registry,
    }

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        report = Report(self.check_type)
        parsing_errors = {}
        self.load_external_checks(external_checks_dir)

        if self.context is None or self.definitions is None or self.breadcrumbs is None:
            self.definitions = {}
            logging.info("Scanning root folder and producing fresh tf_definitions and context")
            if root_folder:
                root_folder = os.path.abspath(root_folder)

                local_graph, tf_definitions = \
                    self.graph_manager.build_graph_from_source_directory(root_folder,
                                                                         local_graph_class=self.graph_class,
                                                                         download_external_modules=runner_filter.download_external_modules,
                                                                         parsing_errors=parsing_errors, excluded_paths=runner_filter.excluded_paths)
            elif files:
                files = [os.path.abspath(file) for file in files]
                root_folder = os.path.split(os.path.commonprefix(files))[0]
                self.parser.evaluate_variables = False
                for file in files:
                    if file.endswith(".tf"):
                        file_parsing_errors = {}
                        parse_result = self.parser.parse_file(file=file, parsing_errors=file_parsing_errors)
                        if parse_result is not None:
                            self.definitions[file] = parse_result
                        if file_parsing_errors:
                            parsing_errors.update(file_parsing_errors)
                            continue
                local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            else:
                raise Exception("Root directory was not specified, files were not specified")

            self.graph_manager.save_graph(local_graph)
            self.definitions, self.breadcrumbs = convert_graph_vertices_to_tf_definitions(local_graph.vertices, root_folder)
        else:
            logging.info(f"Scanning root folder using existing tf_definitions")

        self.check_tf_definition(report, root_folder, runner_filter, collect_skip_comments)

        report.add_parsing_errors(list(parsing_errors.keys()))

        graph_report = self.get_graph_checks_report(root_folder, runner_filter)
        merge_reports(report, graph_report)
        report = remove_duplicate_results(report)

        return report

    def load_external_checks(self, external_checks_dir: List[str]):
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)

    def get_graph_checks_report(self, root_folder, runner_filter: RunnerFilter):
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result['entity']
                entity_context, entity_evaluations = self.get_entity_context_and_evaluations(entity)
                if entity_context:
                    full_file_path = entity[CustomAttributes.FILE_PATH]
                    copy_of_check_result = copy.deepcopy(check_result)
                    for skipped_check in entity_context.get('skipped_checks', []):
                        if skipped_check['id'] == check.id:
                            copy_of_check_result['result'] = CheckResult.SKIPPED
                            copy_of_check_result['suppress_comment'] = skipped_check['suppress_comment']
                            break
                    copy_of_check_result['entity'] = entity.get(CustomAttributes.CONFIG)
                    record = Record(check_id=check.id,
                                    bc_check_id=check.bc_id,
                                    check_name=check.name,
                                    check_result=copy_of_check_result,
                                    code_block=entity_context.get('code_lines'),
                                    file_path=f"/{os.path.relpath(full_file_path, root_folder)}",
                                    file_line_range=[entity_context.get('start_line'),
                                                     entity_context.get('end_line')],
                                    resource=".".join(entity_context['definition_path']),
                                    entity_tags=entity.get('tags', {}),
                                    evaluations=entity_evaluations,
                                    check_class=check.__class__.__module__,
                                    file_abs_path=os.path.abspath(full_file_path))
                    if self.breadcrumbs:
                        breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                        if breadcrumb:
                            record = GraphRecord(record, breadcrumb)

                    report.add_record(record=record)
        return report

    def get_entity_context_and_evaluations(self, entity):
        entity_evaluations = None
        block_type = entity[CustomAttributes.BLOCK_TYPE]
        full_file_path = entity[CustomAttributes.FILE_PATH]
        definition_path = entity[CustomAttributes.BLOCK_NAME].split('.')
        entity_context_path = [block_type] + definition_path
        entity_context = self.context.get(full_file_path, {})
        try:
            if not entity_context:
                dc_keys = self.context.keys()
                dc_key = next(x for x in dc_keys if x.startswith(full_file_path))
                entity_context = self.context.get(dc_key, {})
            for k in entity_context_path:
                if k in entity_context:
                    entity_context = entity_context[k]
                else:
                    logging.warning(f'Failed to find context for {".".join(entity_context_path)}')
                    return None, None
            entity_context['definition_path'] = definition_path
        except StopIteration:
            logging.debug(f"Did not find context for key {full_file_path}")
        return entity_context, entity_evaluations

    def check_tf_definition(self, report, root_folder, runner_filter, collect_skip_comments=True):
        parser_registry.reset_definitions_context()
        if not self.context:
            definitions_context = {}
            for definition in self.definitions.items():
                definitions_context = parser_registry.enrich_definitions_context(definition, collect_skip_comments)
            self.context = definitions_context
            logging.debug('Created definitions context')

        for full_file_path, definition in self.definitions.items():
            abs_scanned_file, abs_referrer = self._strip_module_referrer(full_file_path)
            scanned_file = f"/{os.path.relpath(abs_scanned_file, root_folder)}"
            logging.debug(f"Scanning file: {scanned_file}")
            self.run_all_blocks(definition, self.context, full_file_path, root_folder, report,
                                scanned_file, runner_filter, abs_referrer)

    def run_all_blocks(self, definition, definitions_context, full_file_path, root_folder, report,
                       scanned_file, runner_filter, module_referrer: Optional[str]):
        if not definition:
            logging.debug("Empty definition, skipping run (root_folder=%s)", root_folder)
            return
        block_types = set(definition.keys())
        for block_type in block_types & CHECK_BLOCK_TYPES:
            self.run_block(definition[block_type], definitions_context,
                           full_file_path, root_folder, report,
                           scanned_file, block_type, runner_filter, None, module_referrer)

    def run_block(self, entities,
                  definition_context,
                  full_file_path, root_folder, report, scanned_file,
                  block_type, runner_filter=None, entity_context_path_header=None,
                  module_referrer: Optional[str] = None):

        registry = self.block_type_registries[block_type]
        if not registry:
            return

        for entity in entities:
            entity_evaluations = None
            context_parser = parser_registry.context_parsers[block_type]
            definition_path = context_parser.get_entity_context_path(entity)
            entity_id = ".".join(definition_path)       # example: aws_s3_bucket.my_bucket

            caller_file_path = None
            caller_file_line_range = None

            if module_referrer is not None:
                referrer_id = self._find_id_for_referrer(full_file_path,
                                                         self.definitions)
                if referrer_id:
                    entity_id = f"{referrer_id}.{entity_id}"        # ex: module.my_module.aws_s3_bucket.my_bucket
                    abs_caller_file = module_referrer[:module_referrer.rindex("#")]
                    caller_file_path = f"/{os.path.relpath(abs_caller_file, root_folder)}"

                    try:
                        caller_context = dpath.get(definition_context[abs_caller_file],
                                                   # HACK ALERT: module data is currently double-nested in
                                                   #             definition context. If fixed, remove the
                                                   #             addition of "module." at the beginning.
                                                   "module." + referrer_id,
                                                   separator=".")
                    except KeyError:
                        logging.debug("Unable to find caller context for: %s", abs_caller_file)
                        caller_context = None

                    if caller_context:
                        caller_file_line_range = [caller_context.get('start_line'), caller_context.get('end_line')]
                else:
                    logging.debug(f"Unable to find referrer ID for full path: %s", full_file_path)

            if entity_context_path_header is None:
                entity_context_path = [block_type] + definition_path
            else:
                entity_context_path = entity_context_path_header + block_type + definition_path
            # Entity can exist only once per dir, for file as well
            try:
                entity_context = data_structures_utils.get_inner_dict(definition_context[full_file_path], entity_context_path)
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                skipped_checks = entity_context.get('skipped_checks')
            except KeyError:
                # TODO: Context info isn't working for modules
                entity_lines_range = None
                entity_code_lines = None
                skipped_checks = None

            if full_file_path in self.evaluations_context:
                variables_evaluations = {}
                for var_name, context_info in self.evaluations_context.get(full_file_path, {}).items():
                    variables_evaluations[var_name] = dataclasses.asdict(context_info)
                entity_evaluations = BaseVariableEvaluation.reduce_entity_evaluations(variables_evaluations,
                                                                                      entity_context_path)
            results = registry.scan(scanned_file, entity, skipped_checks, runner_filter)
            absolut_scanned_file_path, _ = self._strip_module_referrer(file_path=full_file_path)
            # This duplicates a call at the start of scan, but adding this here seems better than kludging with some tuple return type
            (entity_type, entity_name, entity_config) = registry.extract_entity_details(entity)
            tags = get_resource_tags(entity_type, entity_config)
            for check, check_result in results.items():
                record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name, check_result=check_result,
                                code_block=entity_code_lines, file_path=scanned_file,
                                file_line_range=entity_lines_range,
                                resource=entity_id, evaluations=entity_evaluations,
                                check_class=check.__class__.__module__, file_abs_path=absolut_scanned_file_path,
                                entity_tags=tags,
                                caller_file_path=caller_file_path,
                                caller_file_line_range=caller_file_line_range)
                breadcrumb = self.breadcrumbs.get(record.file_path, {}).get('.'.join([entity_type, entity_name]))
                if breadcrumb:
                    record = GraphRecord(record, breadcrumb)
                report.add_record(record=record)

    @staticmethod
    def _strip_module_referrer(file_path: str) -> Tuple[str, Optional[str]]:
        """
        For file paths containing module referrer information (e.g.: "module/module.tf[main.tf#0]"), this
        returns a tuple containing the file path (e.g., "module/module.tf") and referrer (e.g., "main.tf#0").
        If the file path does not contain a referred, the tuple will contain the original file path and None.
        """
        if file_path.endswith("]") and "[" in file_path:
            return file_path[:file_path.index("[")], file_path[file_path.index("[") + 1: -1]
        else:
            return file_path, None

    @staticmethod
    def _find_id_for_referrer(full_file_path, definitions) -> Optional[str]:
        for file, file_content in definitions.items():
            if "module" not in file_content:
                continue

            for modules in file_content["module"]:
                for module_name, module_content in modules.items():
                    if "__resolved__" not in module_content:
                        continue

                    if full_file_path in module_content["__resolved__"]:
                        return f"module.{module_name}"
        return None
