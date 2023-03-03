from __future__ import annotations

import copy
import dataclasses
import logging
import os
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, Set, TYPE_CHECKING

import dpath.util

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import ImageReferencerMixin
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.models.enums import CheckResult
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, remove_duplicate_results
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner, CHECKOV_CREATE_GRAPH
from checkov.common.util import data_structures_utils
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.parser_utils import get_module_from_full_path, get_abs_path, \
    get_tf_definition_key_from_module_dependency, TERRAFORM_NESTED_MODULE_PATH_PREFIX, \
    TERRAFORM_NESTED_MODULE_PATH_ENDING, TERRAFORM_NESTED_MODULE_PATH_SEPARATOR_LENGTH, \
    TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR
from checkov.common.util.secrets import omit_secret_value_from_checks, omit_secret_value_from_graph_checks
from checkov.common.variables.context import EvaluationContext
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.utils.dependency_path_handler import PATH_SEPARATOR
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.image_referencer.manager import TerraformImageReferencerManager
from checkov.terraform.parser import Parser
from checkov.terraform.plan_utils import get_resource_id_without_nested_modules
from checkov.terraform.tag_providers import get_resource_tags
from checkov.common.runners.base_runner import strtobool

if TYPE_CHECKING:
    from networkx import DiGraph
    from checkov.common.images.image_referencer import Image

# Allow the evaluation of empty variables
dpath.options.ALLOW_EMPTY_STRING_KEYS = True

CHECK_BLOCK_TYPES = frozenset(['resource', 'data', 'provider', 'module'])


class Runner(ImageReferencerMixin[None], BaseRunner[TerraformGraphManager]):
    check_type = CheckType.TERRAFORM  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        parser: Parser | None = None,
        db_connector: LibraryGraphConnector | None = None,
        external_registries: list[BaseRegistry] | None = None,
        source: str = GraphSource.TERRAFORM,
        graph_class: type[TerraformLocalGraph] = TerraformLocalGraph,
        graph_manager: TerraformGraphManager | None = None
    ) -> None:
        super().__init__(file_extensions=['.tf', '.hcl'])
        self.external_registries = [] if external_registries is None else external_registries
        self.graph_class = graph_class
        self.parser = parser or Parser()
        self.definitions: "dict[str, dict[str, Any]] | None" = None
        self.context = None
        self.breadcrumbs = None
        self.evaluations_context: Dict[str, Dict[str, EvaluationContext]] = {}
        self.graph_manager: TerraformGraphManager = graph_manager if graph_manager is not None else TerraformGraphManager(
            source=source,
            db_connector=db_connector or self.db_connector,
        )
        self.graph_registry = get_graph_checks_registry(self.check_type)
        self.definitions_with_modules: dict[str, dict[str, Any]] = {}
        self.referrer_cache: Dict[str, str] = {}
        self.non_referred_cache: Set[str] = set()
        self.enable_nested_modules = strtobool(os.getenv('CHECKOV_ENABLE_NESTED_MODULES', 'True'))

    block_type_registries = {  # noqa: CCE003  # a static attribute
        'resource': resource_registry,
        'data': data_registry,
        'provider': provider_registry,
        'module': module_registry,
    }

    def run(
            self,
            root_folder: str,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)
        parsing_errors: dict[str, Exception] = {}
        self.load_external_checks(external_checks_dir)
        local_graph = None

        if self.context is None or self.definitions is None or self.breadcrumbs is None:
            self.definitions = {}
            logging.info("Scanning root folder and producing fresh tf_definitions and context")
            if root_folder:
                root_folder = os.path.abspath(root_folder)

                local_graph, self.definitions = self.graph_manager.build_graph_from_source_directory(
                    source_dir=root_folder,
                    local_graph_class=self.graph_class,
                    download_external_modules=runner_filter.download_external_modules,
                    external_modules_download_path=runner_filter.external_modules_download_path,
                    parsing_errors=parsing_errors,
                    excluded_paths=runner_filter.excluded_paths,
                    vars_files=runner_filter.var_files,
                    create_graph=CHECKOV_CREATE_GRAPH,
                )
            elif files:
                files = [os.path.abspath(file) for file in files]
                root_folder = os.path.split(os.path.commonprefix(files))[0]
                self.parser.evaluate_variables = False
                self._parse_files(files, parsing_errors)

                if CHECKOV_CREATE_GRAPH:
                    local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            else:
                raise Exception("Root directory was not specified, files were not specified")

            if CHECKOV_CREATE_GRAPH and local_graph:
                for vertex in local_graph.vertices:
                    if vertex.block_type == BlockType.RESOURCE:
                        if self.enable_nested_modules:
                            vertex_id = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS)
                        else:
                            vertex_id = vertex.id
                        report.add_resource(f'{vertex.path}:{vertex_id}')
                self.graph_manager.save_graph(local_graph)
                self.definitions, self.breadcrumbs = convert_graph_vertices_to_tf_definitions(
                    local_graph.vertices,
                    root_folder,
                )
        else:
            logging.info("Scanning root folder using existing tf_definitions")

        self.pbar.initiate(len(self.definitions))
        self.check_tf_definition(report, root_folder, runner_filter, collect_skip_comments)

        report.add_parsing_errors(parsing_errors.keys())

        if CHECKOV_CREATE_GRAPH:
            graph_report = self.get_graph_checks_report(root_folder, runner_filter)
            merge_reports(report, graph_report)

        report = remove_duplicate_results(report)

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

    def load_external_checks(self, external_checks_dir: list[str] | None) -> None:
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)

    def get_connected_node(self, entity, root_folder) -> Optional[Dict[str, Any]]:
        connected_entity = entity.get('connected_node')
        if not connected_entity:
            return None
        connected_entity_context, connected_entity_evaluations = self.get_entity_context_and_evaluations(
            connected_entity
        )
        if not connected_entity_context:
            return None
        full_file_path = connected_entity[CustomAttributes.FILE_PATH]
        connected_node_data = {}
        connected_node_data['code_block'] = connected_entity_context.get('code_lines')
        connected_node_data['file_path'] = f"/{os.path.relpath(full_file_path, root_folder)}"
        connected_node_data['file_line_range'] = [connected_entity_context.get('start_line'),
                                                  connected_entity_context.get('end_line')]
        connected_node_data['resource'] = ".".join(connected_entity_context['definition_path'])
        connected_node_data['entity_tags'] = connected_entity.get('tags', {})
        connected_node_data['evaluations'] = connected_entity_evaluations
        connected_node_data['file_abs_path'] = os.path.abspath(full_file_path)
        connected_node_data['resource_address'] = connected_entity_context.get('address')
        return connected_node_data

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

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
                    connected_node_data = self.get_connected_node(entity, root_folder)
                    if platform.system() == "Windows":
                        root_folder = os.path.split(full_file_path)[0]
                    resource_id = ".".join(entity_context['definition_path'])
                    resource = resource_id
                    module_dependency = entity.get(CustomAttributes.MODULE_DEPENDENCY)
                    module_dependency_num = entity.get(CustomAttributes.MODULE_DEPENDENCY_NUM)
                    definition_context_file_path = full_file_path
                    if module_dependency and module_dependency_num:
                        if self.enable_nested_modules:
                            resource = entity.get(CustomAttributes.TF_RESOURCE_ADDRESS, resource_id)
                        else:
                            module_dependency_path = module_dependency.split(PATH_SEPARATOR)[-1]
                            tf_path = get_tf_definition_key_from_module_dependency(full_file_path, module_dependency_path, module_dependency_num)
                            referrer_id = self._find_id_for_referrer(tf_path)
                            if referrer_id:
                                resource = f'{referrer_id}.{resource_id}'
                        definition_context_file_path = get_tf_definition_key_from_module_dependency(full_file_path, module_dependency, module_dependency_num)
                    elif entity.get(CustomAttributes.TF_RESOURCE_ADDRESS) and entity.get(CustomAttributes.TF_RESOURCE_ADDRESS) != resource_id:
                        # for plan resources
                        resource = entity[CustomAttributes.TF_RESOURCE_ADDRESS]
                        if not self.enable_nested_modules:
                            resource = get_resource_id_without_nested_modules(resource)
                    entity_config = self.get_graph_resource_entity_config(entity)
                    censored_code_lines = omit_secret_value_from_graph_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_context.get('code_lines'),
                        entity_config=entity_config,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                    )
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=copy_of_check_result,
                        code_block=censored_code_lines,
                        file_path=f"/{os.path.relpath(full_file_path, root_folder)}",
                        file_line_range=[entity_context.get('start_line'),
                                         entity_context.get('end_line')],
                        resource=resource,
                        entity_tags=entity.get('tags', {}),
                        evaluations=entity_evaluations,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(full_file_path),
                        resource_address=entity_context.get('address'),
                        severity=check.severity,
                        bc_category=check.bc_category,
                        benchmarks=check.benchmarks,
                        connected_node=connected_node_data,
                        definition_context_file_path=definition_context_file_path
                    )
                    if self.breadcrumbs:
                        if self.enable_nested_modules:
                            breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(resource)
                        else:
                            breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(resource_id)
                        if breadcrumb:
                            record = GraphRecord(record, breadcrumb)
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)
        return report

    def get_entity_context_and_evaluations(self, entity):
        entity_evaluations = None
        block_type = entity[CustomAttributes.BLOCK_TYPE]
        full_file_path = entity[CustomAttributes.FILE_PATH]
        if entity.get(CustomAttributes.MODULE_DEPENDENCY):
            full_file_path = get_tf_definition_key_from_module_dependency(full_file_path, entity[CustomAttributes.MODULE_DEPENDENCY], entity[CustomAttributes.MODULE_DEPENDENCY_NUM])
        definition_path = entity[CustomAttributes.BLOCK_NAME].split('.')
        entity_context_path = [block_type] + definition_path
        entity_context = self.context.get(full_file_path, {})
        try:
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

    def check_tf_definition(self, report: Report, root_folder: Path, runner_filter: RunnerFilter,
                            collect_skip_comments=True) -> None:
        parser_registry.reset_definitions_context()
        if not self.context:
            definitions_context = {}
            for definition in self.definitions.items():
                definitions_context = parser_registry.enrich_definitions_context(definition, collect_skip_comments)
            self.context = definitions_context
            logging.debug('Created definitions context')

        if self.enable_nested_modules:
            self.push_skipped_checks_down_from_modules(self.context)
        for full_file_path, definition in self.definitions.items():
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(full_file_path, root_folder)})
            if self.enable_nested_modules:
                abs_scanned_file = get_abs_path(full_file_path)
                abs_referrer = None
            else:
                abs_scanned_file, abs_referrer = self._strip_module_referrer(full_file_path)
            scanned_file = f"/{os.path.relpath(abs_scanned_file, root_folder)}"
            logging.debug(f"Scanning file: {scanned_file}")
            self.run_all_blocks(definition, self.context, full_file_path, root_folder, report,
                                scanned_file, runner_filter, abs_referrer)
            self.pbar.update()
        self.pbar.close()

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
            (entity_type, entity_name, entity_config) = registry.extract_entity_details(entity)
            entity_id = ".".join(definition_path)  # example: aws_s3_bucket.my_bucket

            caller_file_path = None
            caller_file_line_range = None

            if self.enable_nested_modules:
                entity_id = entity_config.get(CustomAttributes.TF_RESOURCE_ADDRESS)
                module, _ = get_module_from_full_path(full_file_path)
                if module:
                    full_definition_path = entity_id.split('.')
                    module_name_index = len(full_definition_path) - full_definition_path[::-1][1:].index(BlockType.MODULE) - 1  # the next item after the last 'module' prefix is the module name
                    module_name = full_definition_path[module_name_index]
                    caller_context = definition_context[module].get(BlockType.MODULE, {}).get(module_name)
                    caller_file_line_range = [caller_context.get('start_line'), caller_context.get('end_line')]
                    abs_caller_file = get_abs_path(module)
                    caller_file_path = f"/{os.path.relpath(abs_caller_file, root_folder)}"
            elif module_referrer is not None:
                referrer_id = self._find_id_for_referrer(full_file_path)

                if referrer_id:
                    entity_id = f"{referrer_id}.{entity_id}"  # ex: module.my_module.aws_s3_bucket.my_bucket
                    abs_caller_file = module_referrer[:module_referrer.rindex(TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR)]
                    caller_file_path = f"/{os.path.relpath(abs_caller_file, root_folder)}"

                    try:
                        caller_context = definition_context[abs_caller_file]
                        for part in referrer_id.split("."):
                            caller_context = caller_context[part]
                    except KeyError:
                        logging.debug("Unable to find caller context for: %s", abs_caller_file)
                        caller_context = None

                    if caller_context:
                        caller_file_line_range = [caller_context.get('start_line'), caller_context.get('end_line')]
                else:
                    logging.debug(f"Unable to find referrer ID for full path: {full_file_path}")

            if entity_context_path_header is None:
                entity_context_path = [block_type] + definition_path
            else:
                entity_context_path = entity_context_path_header + block_type + definition_path
            # Entity can exist only once per dir, for file as well
            try:
                entity_context = data_structures_utils.get_inner_dict(
                    definition_context[full_file_path],
                    entity_context_path,
                )
                entity_lines_range = [entity_context.get('start_line'), entity_context.get('end_line')]
                entity_code_lines = entity_context.get('code_lines')
                skipped_checks = entity_context.get('skipped_checks')
            except KeyError:
                # TODO: Context info isn't working for modules
                entity_lines_range = None
                entity_code_lines = None
                skipped_checks = None

            if not self.enable_nested_modules and block_type == "module":
                self.push_skipped_checks_down_old(definition_context, full_file_path, skipped_checks)

            if full_file_path in self.evaluations_context:
                variables_evaluations = {}
                for var_name, context_info in self.evaluations_context.get(full_file_path, {}).items():
                    variables_evaluations[var_name] = dataclasses.asdict(context_info)
                entity_evaluations = BaseVariableEvaluation.reduce_entity_evaluations(variables_evaluations,
                                                                                      entity_context_path)
            results = registry.scan(scanned_file, entity, skipped_checks, runner_filter)
            absolut_scanned_file_path, _ = self._strip_module_referrer(file_path=full_file_path)
            # This duplicates a call at the start of scan, but adding this here seems better than kludging with some tuple return type
            tags = get_resource_tags(entity_type, entity_config)
            if results:
                for check, check_result in results.items():
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
                        evaluations=entity_evaluations,
                        check_class=check.__class__.__module__,
                        file_abs_path=absolut_scanned_file_path,
                        entity_tags=tags,
                        caller_file_path=caller_file_path,
                        caller_file_line_range=caller_file_line_range,
                        severity=check.severity,
                        bc_category=check.bc_category,
                        benchmarks=check.benchmarks,
                        details=check.details,
                        definition_context_file_path=full_file_path
                    )
                    if CHECKOV_CREATE_GRAPH:
                        if self.enable_nested_modules:
                            entity_key = entity_id
                        else:
                            entity_key = f"{entity_type}.{entity_name}"
                        breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(entity_key)
                        if breadcrumb:
                            record = GraphRecord(record, breadcrumb)

                    record.set_guideline(check.guideline)
                    report.add_record(record=record)
            else:
                if block_type == "resource":
                    # resources without checks, but not existing ones
                    report.extra_resources.add(
                        ExtraResource(
                            file_abs_path=absolut_scanned_file_path,
                            file_path=scanned_file,
                            resource=entity_id,
                        )
                    )

    def _parse_files(self, files, parsing_errors):
        def parse_file(file):
            if not (file.endswith(".tf") or file.endswith(".hcl")):
                return
            file_parsing_errors = {}
            parse_result = self.parser.parse_file(file=file, parsing_errors=file_parsing_errors)
            # the exceptions type can un-pickleable so we need to cast them to Exception
            for path, e in file_parsing_errors.items():
                file_parsing_errors[path] = Exception(e.__repr__())
            return file, parse_result, file_parsing_errors

        results = parallel_runner.run_function(parse_file, files)
        for result in results:
            if result:
                file, parse_result, file_parsing_errors = result
                if parse_result is not None:
                    self.definitions[file] = parse_result
                if file_parsing_errors:
                    parsing_errors.update(file_parsing_errors)

    @staticmethod
    def push_skipped_checks_down_old(definition_context, module_path, skipped_checks):
        # this method pushes the skipped_checks down the 1 level to all resource types.

        if skipped_checks is None:
            return

        if len(skipped_checks) == 0:
            return

        # iterate over definitions to find those that reference the module path
        # definition is in the format <file>[<referrer>#<index>]
        # where referrer could be a path, or path1->path2, etc

        for definition in definition_context:
            _, mod_ref = Runner._strip_module_referrer(definition)
            if mod_ref is None:
                continue

            if module_path not in mod_ref:
                continue

            for block_type, block_configs in definition_context[definition].items():
                # skip if type is not a Terraform resource
                if block_type not in CHECK_BLOCK_TYPES:
                    continue

                if block_type == "module":
                    # modules don't have a type, just a name
                    for resource_config in block_configs.values():
                        # append the skipped checks also from a module to another module
                        resource_config["skipped_checks"] += skipped_checks
                else:
                    # there may be multiple resource types - aws_bucket, etc
                    for resource_configs in block_configs.values():
                        # there may be multiple names for each resource type
                        for resource_config in resource_configs.values():
                            # append the skipped checks from the module to the other resources.
                            resource_config["skipped_checks"] += skipped_checks

    def push_skipped_checks_down_from_modules(self, definition_context):
        module_context_parser = parser_registry.context_parsers[BlockType.MODULE]
        for full_file_path, definition in self.definitions.items():
            definition_modules_context = definition_context.get(full_file_path, {}).get(BlockType.MODULE, {})
            for entity in definition.get(BlockType.MODULE, []):
                module_name = module_context_parser.get_entity_context_path(entity)[0]
                skipped_checks = definition_modules_context.get(module_name).get('skipped_checks')
                resolved_paths = entity.get(module_name).get(RESOLVED_MODULE_ENTRY_NAME)
                self.push_skipped_checks_down(definition_context, skipped_checks, resolved_paths)

    def push_skipped_checks_down(self, definition_context, skipped_checks, resolved_paths):
        # this method pushes the skipped_checks down the 1 level to all resource types.
        if not skipped_checks:
            return

        for definition in resolved_paths:
            for block_type, block_configs in definition_context.get(definition, {}).items():
                # skip if type is not a Terraform resource
                if block_type not in CHECK_BLOCK_TYPES:
                    continue

                if block_type == "module":
                    # modules don't have a type, just a name
                    for module_name, module_config in block_configs.items():
                        # append the skipped checks also from a module to another module
                        module_config["skipped_checks"] += skipped_checks
                        module_context = next(m for m in self.definitions.get(definition).get(block_type) if module_name in m)
                        recursive_resolved_paths = module_context.get(module_name).get(RESOLVED_MODULE_ENTRY_NAME)
                        self.push_skipped_checks_down(definition_context, skipped_checks, recursive_resolved_paths)
                else:
                    # there may be multiple resource types - aws_bucket, etc
                    for resource_configs in block_configs.values():
                        # there may be multiple names for each resource type
                        for resource_config in resource_configs.values():
                            # append the skipped checks from the module to the other resources.
                            resource_config["skipped_checks"] += skipped_checks

    @staticmethod
    def _strip_module_referrer(file_path: str) -> Tuple[str, Optional[str]]:
        """
        For file paths containing module referrer information (e.g.: "module/module.tf[main.tf#0]"), this
        returns a tuple containing the file path (e.g., "module/module.tf") and referrer (e.g., "main.tf#0").
        If the file path does not contain a referred, the tuple will contain the original file path and None.
        """
        if file_path.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING) and TERRAFORM_NESTED_MODULE_PATH_PREFIX in file_path:
            return file_path[:file_path.index(TERRAFORM_NESTED_MODULE_PATH_PREFIX)], \
                file_path[file_path.index(TERRAFORM_NESTED_MODULE_PATH_PREFIX) + TERRAFORM_NESTED_MODULE_PATH_SEPARATOR_LENGTH: -TERRAFORM_NESTED_MODULE_PATH_SEPARATOR_LENGTH]
        else:
            return file_path, None

    def _find_id_for_referrer(self, full_file_path) -> Optional[str]:
        cached_referrer = self.referrer_cache.get(full_file_path)
        if cached_referrer:
            return cached_referrer
        if full_file_path in self.non_referred_cache:
            return None

        if not self.definitions_with_modules:
            self._prepare_definitions_with_modules()
        for file_content in self.definitions_with_modules.values():
            for modules in file_content["module"]:
                for module_name, module_content in modules.items():
                    if RESOLVED_MODULE_ENTRY_NAME not in module_content:
                        continue

                    if full_file_path in module_content[RESOLVED_MODULE_ENTRY_NAME]:
                        id_referrer = f"module.{module_name}"
                        self.referrer_cache[full_file_path] = id_referrer
                        return id_referrer

        self.non_referred_cache.add(full_file_path)
        return None

    def _prepare_definitions_with_modules(self) -> None:
        def __cache_file_content(file_name: str, file_modules: list[dict[str, Any]]) -> None:
            for modules in file_modules:
                for module_content in modules.values():
                    if RESOLVED_MODULE_ENTRY_NAME in module_content:
                        self.definitions_with_modules[file_name] = file_content
                        return

        for file, file_content in self.definitions.items():
            if "module" in file_content:
                __cache_file_content(file_name=file, file_modules=file_content["module"])

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        if not graph_connector:
            # should not happen
            return []

        manager = TerraformImageReferencerManager(graph_connector=graph_connector)
        images = manager.extract_images_from_resources()

        return images

    @staticmethod
    def get_graph_resource_entity_config(entity):
        context_parser = parser_registry.context_parsers[entity[CustomAttributes.BLOCK_TYPE]]
        entity_config = entity[CustomAttributes.CONFIG]
        definition_path = context_parser.get_entity_definition_path(entity_config)
        for path in definition_path:
            entity_config = entity_config[path]
        return entity_config
