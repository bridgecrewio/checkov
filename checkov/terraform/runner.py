from __future__ import annotations

import dataclasses
import logging
import os
from typing import Any, TYPE_CHECKING, Optional

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, remove_duplicate_results
from checkov.common.util import data_structures_utils
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform import get_module_from_full_path, get_module_name, get_abs_path
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.runner_filter import RunnerFilter
from checkov.terraform.base_runner import BaseTerraformRunner
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.modules.module_objects import TFDefinitionKey, TFModule
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.tag_providers import get_resource_tags
from checkov.common.runners.base_runner import strtobool
from checkov.terraform.tf_parser import TFParser

if TYPE_CHECKING:
    from checkov.common.typing import _SkippedCheck, LibraryGraph, LibraryGraphConnector

_TerraformContext: TypeAlias = "dict[TFDefinitionKey, dict[str, Any]]"
_TerraformDefinitions: TypeAlias = "dict[TFDefinitionKey, dict[str, Any]]"

CHECK_BLOCK_TYPES = frozenset(["resource", "data", "provider", "module"])


class Runner(BaseTerraformRunner[_TerraformDefinitions, _TerraformContext, TFDefinitionKey]):
    check_type = CheckType.TERRAFORM  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        parser: TFParser | None = None,
        db_connector: LibraryGraphConnector | None = None,
        external_registries: list[BaseRegistry] | None = None,
        source: str = GraphSource.TERRAFORM,
        graph_class: type[TerraformLocalGraph] = TerraformLocalGraph,
        graph_manager: TerraformGraphManager | None = None,
    ) -> None:
        super().__init__(parser, db_connector, external_registries, source, graph_class, graph_manager)
        self.all_graphs: list[tuple[LibraryGraph, Optional[str]]] = []

    def run(
        self,
        root_folder: str | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)
        parsing_errors: dict[str, Exception] = {}
        self.load_external_checks(external_checks_dir)
        if self.context is None or self.definitions is None or self.breadcrumbs is None:
            self.definitions = {}
            logging.info("Scanning root folder and producing fresh tf_definitions and context")
            tf_split_graph = strtobool(os.getenv("TF_SPLIT_GRAPH", "False"))
            if root_folder:
                root_folder = os.path.abspath(root_folder)
                if tf_split_graph:
                    graphs_with_definitions, self.resource_subgraph_map = self.graph_manager.build_multi_graph_from_source_directory(
                        source_dir=root_folder,
                        local_graph_class=self.graph_class,
                        download_external_modules=runner_filter.download_external_modules,
                        external_modules_download_path=runner_filter.external_modules_download_path,
                        parsing_errors=parsing_errors,
                        excluded_paths=runner_filter.excluded_paths,
                        vars_files=runner_filter.var_files,
                    )
                    local_graphs: list[tuple[str | None, TerraformLocalGraph]] = []
                    for graph, definitions, subgraph_path in graphs_with_definitions:
                        for definition in definitions:
                            self.definitions.update(definition)
                        local_graphs.append((subgraph_path, graph))
                else:
                    single_graph, self.definitions = self.graph_manager.build_graph_from_source_directory(
                        source_dir=root_folder,
                        local_graph_class=self.graph_class,
                        download_external_modules=runner_filter.download_external_modules,
                        parsing_errors=parsing_errors,
                        excluded_paths=runner_filter.excluded_paths,
                        external_modules_download_path=runner_filter.external_modules_download_path,
                        vars_files=runner_filter.var_files,
                    )
                    # Make graph a list to allow single processing method for all cases
                    local_graphs = [(None, single_graph)]
            elif files:
                files = [os.path.abspath(file) for file in files]
                root_folder = os.path.split(os.path.commonprefix(files))[0]
                self._parse_files(files, parsing_errors)

                if tf_split_graph:
                    local_graphs = self.graph_manager.build_multi_graph_from_definitions(self.definitions)
                else:
                    # local_graph needs to be a list to allow supporting multi graph
                    local_graphs = [(None, self.graph_manager.build_graph_from_definitions(self.definitions))]
            else:
                raise Exception("Root directory was not specified, files were not specified")

            if local_graphs:
                self._update_definitions_and_breadcrumbs(
                    local_graphs,
                    report,
                    root_folder)
        else:
            logging.info("Scanning root folder using existing tf_definitions")
            if root_folder is None:
                # this shouldn't happen
                raise Exception("Root directory was not specified")

        self.pbar.initiate(len(self.definitions))
        self.check_tf_definition(report, root_folder, runner_filter, collect_skip_comments)

        report.add_parsing_errors(parsing_errors.keys())

        if self.all_graphs:
            for single_graph, _ in self.all_graphs:  # type: ignore  # Due to issue with rustworkx typing
                graph_report = self.get_graph_checks_report(root_folder, runner_filter, graph=single_graph)
                merge_reports(report, graph_report)
        else:
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

    def _parse_files(self, files: list[str], parsing_errors: dict[str, Exception]) -> None:
        if self.definitions is None:
            # just make sure it is not 'None'
            self.definitions = {}

        results = parallel_runner.run_function(self.parse_file, files)
        for result in results:
            if result:
                file, parse_result, file_parsing_errors = result
                if parse_result is not None:
                    self.definitions[TFDefinitionKey(file_path=file)] = parse_result
                if file_parsing_errors:
                    parsing_errors.update(file_parsing_errors)

    def parse_file(self, file: str) -> tuple[str, dict[str, Any] | None, dict[str, Exception]] | None:
        if not (file.endswith(".tf") or file.endswith(".hcl")):
            return None
        file_parsing_errors: dict[str, Exception] = {}
        parse_result = self.parser.parse_file(file=file, parsing_errors=file_parsing_errors)
        # the exceptions type can un-pickleable so we need to cast them to Exception
        for path, e in file_parsing_errors.items():
            file_parsing_errors[path] = Exception(e.__repr__())
        return file, parse_result, file_parsing_errors

    def _update_definitions_and_breadcrumbs(
        self, local_graphs: list[tuple[Optional[str], TerraformLocalGraph]], report: Report, root_folder: str
    ) -> None:
        self.definitions = {}
        self.breadcrumbs = {}
        self.all_graphs = []
        for subgraph_path, local_graph in local_graphs:
            for vertex in local_graph.vertices:
                if vertex.block_type == BlockType.RESOURCE:
                    vertex_id = vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS)
                    report.add_resource(f"{vertex.path}:{vertex_id}")
            graph = self.graph_manager.save_graph(local_graph)
            self.all_graphs.append((graph, subgraph_path))
            current_definitions, current_breadcrumbs = convert_graph_vertices_to_tf_definitions(
                local_graph.vertices,
                root_folder,
            )
            self.definitions.update(current_definitions)
            self.breadcrumbs.update(current_breadcrumbs)

    def check_tf_definition(
        self,
        report: Report,
        root_folder: str,
        runner_filter: RunnerFilter,
        collect_skip_comments: bool = True,
    ) -> None:
        parser_registry.reset_definitions_context()
        if not self.definitions:
            # nothing to do
            self.pbar.update()
            self.pbar.close()
            return

        if not self.context:
            definitions_context = {}
            for definition_key_tuple in self.definitions.items():
                definitions_context = parser_registry.enrich_definitions_context(
                    definitions=definition_key_tuple, collect_skip_comments=collect_skip_comments
                )
            self.context = definitions_context
            logging.debug("Created definitions context")

        self.push_skipped_checks_down_from_modules(self.context)
        for full_file_path, definition in self.definitions.items():
            self.pbar.set_additional_data({"Current File Scanned": os.path.relpath(full_file_path.file_path)})
            abs_scanned_file = get_abs_path(full_file_path)
            abs_referrer = None
            scanned_file = f"{os.sep}{os.path.relpath(abs_scanned_file, root_folder)}"
            logging.debug(f"Scanning file: {scanned_file}")
            self.run_all_blocks(
                definition, self.context, full_file_path, root_folder, report, scanned_file, runner_filter, abs_referrer
            )
            self.pbar.update()
        self.pbar.close()

    def push_skipped_checks_down_from_modules(self, definition_context: dict[TFDefinitionKey, dict[str, Any]]) -> None:
        if not self.definitions:
            # no need to proceed
            return

        module_context_parser = parser_registry.context_parsers[BlockType.MODULE]
        for tf_definition_key, definition in self.definitions.items():
            full_file_path = tf_definition_key
            definition_modules_context = definition_context.get(full_file_path, {}).get(BlockType.MODULE, {})
            for entity in definition.get(BlockType.MODULE, []):
                module_name = module_context_parser.get_entity_context_path(entity)[0]
                skipped_checks = definition_modules_context.get(module_name, {}).get("skipped_checks")
                resolved_paths = entity.get(module_name).get(RESOLVED_MODULE_ENTRY_NAME)
                self.push_skipped_checks_down(definition_context, skipped_checks, resolved_paths)

    def push_skipped_checks_down(
        self,
        definition_context: dict[TFDefinitionKey, dict[str, Any]],
        skipped_checks: list[_SkippedCheck],
        resolved_paths: list[TFDefinitionKey],
    ) -> None:
        # this method pushes the skipped_checks down the 1 level to all resource types.
        if not skipped_checks or not resolved_paths:
            return
        for ind, definition in enumerate(resolved_paths):
            for block_type, block_configs in definition_context.get(definition, {}).items():
                # skip if type is not a Terraform resource
                if block_type not in CHECK_BLOCK_TYPES:
                    continue

                if block_type == "module":
                    if not self.definitions:
                        # no need to proceed
                        continue

                    # modules don't have a type, just a name
                    for module_name, module_config in block_configs.items():
                        # append the skipped checks also from a module to another module
                        module_config["skipped_checks"] += skipped_checks
                        module_context = next(
                            m
                            for m in self.definitions.get(resolved_paths[ind], {}).get(block_type, [])
                            if module_name in m
                        )
                        recursive_resolved_paths = module_context.get(module_name).get(RESOLVED_MODULE_ENTRY_NAME)
                        self.push_skipped_checks_down(definition_context, skipped_checks, recursive_resolved_paths)
                else:
                    # there may be multiple resource types - aws_bucket, etc
                    for resource_configs in block_configs.values():
                        # there may be multiple names for each resource type
                        for resource_config in resource_configs.values():
                            # append the skipped checks from the module to the other resources.
                            resource_config["skipped_checks"] += skipped_checks

    def run_all_blocks(
        self,
        definition: dict[str, list[dict[str, Any]]],
        definitions_context: _TerraformContext,
        full_file_path: TFDefinitionKey,
        root_folder: str,
        report: Report,
        scanned_file: str,
        runner_filter: RunnerFilter,
        module_referrer: str | None,
    ) -> None:
        if not definition:
            logging.debug(f"Empty definition, skipping run (root_folder={root_folder})")
            return
        block_types = set(definition.keys())
        for block_type in block_types & CHECK_BLOCK_TYPES:
            self.run_block(
                definition[block_type],
                definitions_context,
                full_file_path,
                root_folder,
                report,
                scanned_file,
                block_type,
                runner_filter,
                None,
                module_referrer,
            )

    def run_block(
        self,
        entities: list[dict[str, Any]],
        definition_context: _TerraformContext,
        full_file_path: TFDefinitionKey,
        root_folder: str,
        report: Report,
        scanned_file: str,
        block_type: str,
        runner_filter: RunnerFilter,
        entity_context_path_header: str | None = None,
        module_referrer: str | None = None,
    ) -> None:
        registry = self.block_type_registries[block_type]
        if not registry:
            return

        for entity in entities:
            entity_evaluations = None
            context_parser = parser_registry.context_parsers[block_type]
            definition_path = context_parser.get_entity_context_path(entity)
            (entity_type, entity_name, entity_config) = registry.extract_entity_details(entity)

            caller_file_path = None
            caller_file_line_range = None

            entity_id = entity_config.get(CustomAttributes.TF_RESOURCE_ADDRESS)
            module_full_path, _ = get_module_from_full_path(full_file_path)
            if module_full_path:
                module_name = get_module_name(full_file_path)
                if not module_name:
                    full_definition_path = entity_id.split(".")
                    try:
                        module_name_index = (
                            len(full_definition_path) - full_definition_path[::-1][1:].index(BlockType.MODULE) - 1
                        )  # the next item after the last 'module' prefix is the module name
                    except ValueError as e:
                        # TODO handle multiple modules with the same name in repo
                        logging.warning(f"Failed to get module name for resource {entity_id}. {str(e)}")
                        continue
                    module_name = full_definition_path[module_name_index]
                caller_context = definition_context.get(module_full_path, {}).get(BlockType.MODULE, {}).get(module_name)
                if not caller_context:
                    continue
                caller_file_line_range = (caller_context.get("start_line", 1), caller_context.get("end_line", 1))
                abs_caller_file = get_abs_path(module_full_path)
                caller_file_path = f"{os.sep}{os.path.relpath(abs_caller_file, root_folder)}"

            if entity_context_path_header is None:
                entity_context_path = [block_type] + definition_path
            else:
                # TODO: check, if this code part is still used
                entity_context_path = [entity_context_path_header, block_type] + definition_path
            # Entity can exist only once per dir, for file as well
            context_path = full_file_path
            try:
                entity_context = data_structures_utils.get_inner_dict(
                    definition_context[context_path],
                    entity_context_path,
                )
                entity_lines_range = [entity_context.get("start_line", 1), entity_context.get("end_line", 1)]
                entity_code_lines = entity_context.get("code_lines", [])
                skipped_checks = entity_context.get("skipped_checks")
            except KeyError:
                # TODO: Context info isn't working for modules
                entity_lines_range = [1, 1]
                entity_code_lines = []
                skipped_checks = None

            if full_file_path in self.evaluations_context:
                variables_evaluations = {}
                for var_name, context_info in self.evaluations_context.get(full_file_path, {}).items():
                    variables_evaluations[var_name] = dataclasses.asdict(context_info)
                entity_evaluations = BaseVariableEvaluation.reduce_entity_evaluations(
                    variables_evaluations, entity_context_path
                )
            self._assign_correct_graph_to_registry(registry, scanned_file)
            results = registry.scan(scanned_file, entity, skipped_checks, runner_filter)
            absolute_scanned_file_path = get_abs_path(full_file_path)
            # This duplicates a call at the start of scan, but adding this here seems better than kludging with some tuple return type
            tags = get_resource_tags(entity_type, entity_config)
            if results:
                for check, check_result in results.items():
                    censored_code_lines = omit_secret_value_from_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_code_lines,
                        entity_config=entity_config,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit,
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
                        file_abs_path=absolute_scanned_file_path,
                        entity_tags=tags,
                        caller_file_path=caller_file_path,
                        caller_file_line_range=caller_file_line_range,
                        severity=check.severity,
                        bc_category=check.bc_category,
                        benchmarks=check.benchmarks,
                        details=check.details,
                        definition_context_file_path=full_file_path.file_path,
                    )
                    if self.breadcrumbs:
                        entity_key = entity_id
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
                            file_abs_path=absolute_scanned_file_path,
                            file_path=scanned_file,
                            resource=entity_id,
                        )
                    )

    def _assign_correct_graph_to_registry(self, registry: BaseCheckRegistry, scanned_file: str) -> None:
        registry.graph = None
        if self.all_graphs and isinstance(self.all_graphs, list):
            if len(self.all_graphs) == 1:
                graph_obj = self.all_graphs[0]
                if graph_obj and isinstance(graph_obj, tuple):
                    registry.graph = graph_obj[0]  # type: ignore[assignment]
            else:
                for graph_obj in self.all_graphs:
                    if isinstance(graph_obj, tuple) and isinstance(graph_obj[1], str) and scanned_file.startswith(graph_obj[1]):
                        registry.graph = graph_obj[0]  # type: ignore[assignment]
                        break

    def get_entity_context_and_evaluations(self, entity: dict[str, Any]) -> dict[str, Any] | None:
        block_type = entity[CustomAttributes.BLOCK_TYPE]
        tf_source_module_obj = entity.get(CustomAttributes.SOURCE_MODULE_OBJECT)
        if isinstance(tf_source_module_obj, dict):
            tf_source_module_obj = TFModule.from_json(tf_source_module_obj)
        full_file_path = TFDefinitionKey(
            file_path=entity[CustomAttributes.FILE_PATH], tf_source_modules=tf_source_module_obj
        )

        definition_path = entity[CustomAttributes.BLOCK_NAME].split(".")
        entity_context_path = [block_type] + definition_path
        try:
            entity_context = self.context[full_file_path]  # type:ignore[index]  # at this point self.context is set
            for k in entity_context_path:
                if k in entity_context:
                    entity_context = entity_context[k]
                else:
                    logging.warning(f'Failed to find context for {".".join(entity_context_path)}')
                    return None
            entity_context["definition_path"] = definition_path
        except KeyError:
            logging.error(f"Did not find context for key {full_file_path}")
            return {}
        return entity_context
