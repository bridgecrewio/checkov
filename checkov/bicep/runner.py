from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import cast, Type, TYPE_CHECKING, Any, Literal

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.bicep.graph_builder.context_definitions import build_definitions_context
from checkov.bicep.checks.param.registry import registry as param_registry
from checkov.bicep.checks.resource.registry import registry as resource_registry
from checkov.bicep.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.bicep.graph_builder.local_graph import BicepLocalGraph
from checkov.bicep.graph_manager import BicepGraphManager
from checkov.bicep.image_referencer.manager import BicepImageReferencerManager
from checkov.bicep.parser import Parser
from checkov.bicep.utils import clean_file_path, get_scannable_file_paths
from checkov.common.checks_infra.registry import get_graph_checks_registry

from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import ImageReferencerMixin
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.typing import _CheckResult
from checkov.common.util.secrets import omit_secret_value_from_checks
from checkov.common.util.suppression import collect_suppressions_for_report
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.checks_infra.registry import Registry
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph
    from pycep.typing import BicepJson

_BicepContext: TypeAlias = "dict[str, dict[str, Any]]"
_BicepDefinitions: TypeAlias = "dict[Path, BicepJson]"


class Runner(ImageReferencerMixin[None], BaseRunner[_BicepDefinitions, _BicepContext, BicepGraphManager]):
    check_type = CheckType.BICEP  # noqa: CCE003  # a static attribute

    block_type_registries: 'dict[Literal["parameters", "resources"], BaseCheckRegistry]' = {  # noqa: CCE003  # a static attribute
        "parameters": param_registry,
        "resources": resource_registry,
    }

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.BICEP,
        graph_class: Type[BicepLocalGraph] = BicepLocalGraph,
        graph_manager: BicepGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None
    ) -> None:
        super().__init__(file_extensions=['.bicep'])
        db_connector = db_connector or self.db_connector
        self.external_registries = external_registries if external_registries else []
        self.graph_class = graph_class
        self.graph_manager: BicepGraphManager = (
            graph_manager if graph_manager else BicepGraphManager(source=source, db_connector=db_connector)
        )
        self.graph_registry: Registry = get_graph_checks_registry(self.check_type)

        self.context: _BicepContext = {}
        self.definitions: _BicepDefinitions = {}
        self.definitions_raw: dict[Path, list[tuple[int, str]]] = {}    # type:ignore[assignment]
        self.root_folder: str | Path | None = None

    def run(
        self,
        root_folder: str | Path | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(Runner.check_type)
        self.root_folder = root_folder

        if not self.context or not self.definitions:
            file_paths = get_scannable_file_paths(
                root_folder=root_folder, files=files, excluded_paths=runner_filter.excluded_paths
            )

            if not file_paths:
                return report

            self.definitions, self.definitions_raw, parsing_errors = Parser().get_files_definitions(file_paths)

            report.add_parsing_errors(parsing_errors)

            if external_checks_dir:
                for directory in external_checks_dir:
                    resource_registry.load_external_checks(directory)
                    self.graph_registry.load_external_checks(directory)

            self.context = build_definitions_context(definitions=self.definitions, definitions_raw=self.definitions_raw)

            logging.info("Creating Bicep graph")
            local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            logging.info("Successfully created Bicep graph")

            self.graph_manager.save_graph(local_graph)
            self.definitions, self.breadcrumbs = convert_graph_vertices_to_tf_definitions(
                vertices=local_graph.vertices, root_folder=root_folder
            )

        self.pbar.initiate(len(self.definitions))

        # run Python checks
        self.add_python_check_results(report=report, runner_filter=runner_filter, root_folder=root_folder)

        # run graph checks
        self.add_graph_check_results(report=report, runner_filter=runner_filter)

        if runner_filter.run_image_referencer:
            if files:
                # 'root_folder' shouldn't be empty to remove the whole path later and only leave the shortened form
                root_folder = os.path.split(os.path.commonprefix(files))[0]

            image_report = self.check_container_image_references(
                graph_connector=self.graph_manager.get_reader_endpoint(),
                root_path=root_folder,
                runner_filter=runner_filter,
            )

            if image_report:
                # due too many tests failing only return a list, if there is an image report
                return [report, image_report]

        return report

    def set_definitions_raw(self, definitions_raw: dict[Path, list[tuple[int, str]]]) -> None:
        self.definitions_raw = definitions_raw

    def add_python_check_results(
        self, report: Report, runner_filter: RunnerFilter, root_folder: str | Path | None
    ) -> None:
        """Adds Python check results to given report"""

        for file_path, definition in self.definitions.items():
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(file_path, root_folder)})
            for block_type, registry in Runner.block_type_registries.items():
                block_type_confs = definition.get(block_type)
                if block_type_confs:
                    for name, conf in block_type_confs.items():
                        results = registry.scan(
                            scanned_file=str(file_path),
                            entity={name: conf},
                            skipped_checks=[],
                            runner_filter=runner_filter
                        )

                        if results:
                            file_code_lines = self.definitions_raw[file_path]
                            start_line = conf["__start_line__"]
                            end_line = conf["__end_line__"]

                            cleaned_path = clean_file_path(file_path)
                            resource_id = f"{conf['type']}.{name}"
                            report.add_resource(f"{cleaned_path}:{resource_id}")

                            suppressions = collect_suppressions_for_report(
                                code_lines=file_code_lines[start_line - 1 : end_line]
                            )

                            for check, check_result in results.items():
                                if check.id in suppressions.keys():
                                    check_result = suppressions[check.id]
                                elif check.bc_id and check.bc_id in suppressions.keys():
                                    check_result = suppressions[check.bc_id]

                                censored_code_lines = omit_secret_value_from_checks(
                                    check=check,
                                    check_result=check_result,
                                    entity_code_lines=file_code_lines[start_line - 1 : end_line],
                                    entity_config=conf,
                                    resource_attributes_to_omit=runner_filter.resource_attr_to_omit
                                )

                                record = Record(
                                    check_id=check.id,
                                    bc_check_id=check.bc_id,
                                    check_name=check.name,
                                    check_result=check_result,
                                    code_block=censored_code_lines,
                                    file_path=self.extract_file_path_from_abs_path(cleaned_path),
                                    file_line_range=[start_line, end_line],
                                    resource=resource_id,
                                    check_class=check.__class__.__module__,
                                    file_abs_path=str(file_path.absolute()),
                                    evaluations=None,
                                    severity=check.severity,
                                )
                                record.set_guideline(check.guideline)
                                report.add_record(record=record)
                        elif conf.get("existing") is False:
                            # resources without checks, but not existing ones

                            cleaned_path = clean_file_path(file_path)
                            resource_id = f"{conf['type']}.{name}"
                            report.extra_resources.add(
                                ExtraResource(
                                    file_abs_path=str(file_path.absolute()),
                                    file_path=self.extract_file_path_from_abs_path(cleaned_path),
                                    resource=resource_id,
                                )
                            )
            self.pbar.update()
        self.pbar.close()

    def extract_file_path_from_abs_path(self, path: Path) -> str:
        return f"/{os.path.relpath(path, self.root_folder)}"

    def add_graph_check_results(self, report: Report, runner_filter: RunnerFilter) -> None:
        """Adds YAML check results to given report"""

        checks_results = self.run_graph_checks_results(runner_filter, self.check_type)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path = Path(entity[CustomAttributes.FILE_PATH])

                clean_check_result: _CheckResult = {
                    "result": check_result["result"],
                    "evaluated_keys": check_result["evaluated_keys"],
                }

                file_code_lines = self.definitions_raw[entity_file_path]
                start_line = entity["__start_line__"]
                end_line = cast("int", entity["__end_line__"])

                record = Record(
                    check_id=check.id,
                    bc_check_id=check.bc_id,
                    check_name=check.name,
                    check_result=clean_check_result,
                    code_block=file_code_lines[start_line - 1 : end_line],
                    file_path=self.extract_file_path_from_abs_path(clean_file_path(entity_file_path)),
                    file_line_range=[start_line, end_line],
                    resource=entity[CustomAttributes.ID],
                    check_class=check.__class__.__module__,
                    file_abs_path=str(entity_file_path.absolute()),
                    evaluations=None,
                    severity=check.severity,
                )
                if self.breadcrumbs:
                    breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(record.resource)
                    if breadcrumb:
                        record = GraphRecord(record, breadcrumb)
                record.set_guideline(check.guideline)
                report.add_record(record=record)

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None,
    ) -> list[Image]:
        if not graph_connector:
            # should not happen
            return []

        manager = BicepImageReferencerManager(graph_connector=graph_connector)
        images = manager.extract_images_from_resources()

        return images
