from __future__ import annotations

import os
import platform
from abc import abstractmethod
from typing import Dict, Optional, Any, Set, TYPE_CHECKING, TypeVar, Generic

import dpath
from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import ImageReferencerMixin
from checkov.common.models.enums import CheckResult
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.secrets import omit_secret_value_from_graph_checks
from checkov.common.variables.context import EvaluationContext
from checkov.runner_filter import RunnerFilter
from checkov.terraform.modules.module_objects import TFDefinitionKey
from checkov.terraform.checks.data.registry import data_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.image_referencer.manager import TerraformImageReferencerManager
from checkov.terraform.tag_providers import get_resource_tags
from checkov.terraform.tf_parser import TFParser
from checkov.common.util.env_vars_config import env_vars_config

if TYPE_CHECKING:
    from networkx import DiGraph
    from checkov.common.checks_infra.registry import Registry
    from checkov.common.images.image_referencer import Image
    from checkov.common.typing import LibraryGraphConnector, LibraryGraph

_Context = TypeVar("_Context", bound="dict[Any, Any]|None")
_Definitions = TypeVar("_Definitions", bound="dict[Any, Any]|None")
_FilePath = TypeVar("_FilePath")

# Allow the evaluation of empty variables
dpath.options.ALLOW_EMPTY_STRING_KEYS = True


class BaseTerraformRunner(
    ImageReferencerMixin[None],
    BaseRunner[_Definitions, _Context, TerraformGraphManager],
    Generic[_Definitions, _Context, _FilePath],
):
    def __init__(
        self,
        parser: TFParser | None = None,
        db_connector: LibraryGraphConnector | None = None,
        external_registries: list[BaseRegistry] | None = None,
        source: str = GraphSource.TERRAFORM,
        graph_class: type[TerraformLocalGraph] = TerraformLocalGraph,
        graph_manager: TerraformGraphManager | None = None,
    ) -> None:
        super().__init__(file_extensions=[".tf", ".hcl"])
        self.external_registries = [] if external_registries is None else external_registries
        self.graph_class = graph_class
        self.parser = parser or TFParser()
        self.definitions: _Definitions | None = None
        self.context: _Context | None = None
        self.breadcrumbs = None
        self.evaluations_context: Dict[TFDefinitionKey, Dict[str, EvaluationContext]] = {}
        self.graph_manager: TerraformGraphManager = (
            graph_manager
            if graph_manager is not None
            else TerraformGraphManager(
                source=source,
                db_connector=db_connector or self.db_connector,
            )
        )
        self.graph_registry: Registry = get_graph_checks_registry(self.check_type)
        self.definitions_with_modules: dict[str, dict[str, Any]] = {}
        self.referrer_cache: Dict[str, str] = {}
        self.non_referred_cache: Set[str] = set()

    block_type_registries = {  # noqa: CCE003  # a static attribute
        "resource": resource_registry,
        "data": data_registry,
        "provider": provider_registry,
        "module": module_registry,
    }

    @abstractmethod
    def run(
        self,
        root_folder: str | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        pass

    def load_external_checks(self, external_checks_dir: list[str] | None) -> None:
        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)
                self.graph_registry.load_external_checks(directory)

    def _get_connected_node_data(self, connected_node: dict[str, Any], root_folder: str) \
            -> Optional[Dict[str, Any]]:
        if not connected_node:
            return None
        connected_entity_context = self.get_entity_context_and_evaluations(connected_node)
        if not connected_entity_context:
            return None
        full_file_path = connected_node[CustomAttributes.FILE_PATH]
        connected_node_data = {}
        connected_node_data["code_block"] = connected_entity_context.get("code_lines")
        connected_node_data["file_path"] = f"{os.sep}{os.path.relpath(full_file_path, root_folder)}"
        connected_node_data["file_line_range"] = [
            connected_entity_context.get("start_line"),
            connected_entity_context.get("end_line"),
        ]
        connected_node_data["resource"] = ".".join(connected_entity_context["definition_path"])
        connected_node_data["entity_tags"] = connected_node.get("tags", {})
        connected_node_data["evaluations"] = None
        connected_node_data["file_abs_path"] = os.path.abspath(full_file_path)
        connected_node_data["resource_address"] = connected_entity_context.get("address")
        return connected_node_data

    def get_graph_checks_report(
        self, root_folder: str, runner_filter: RunnerFilter, graph: LibraryGraph | None = None
    ) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter, self.check_type, graph)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_context = self.get_entity_context_and_evaluations(entity)
                virtual_resources = entity.get(CustomAttributes.CONFIG, {}).get('virtual_resources')
                if (env_vars_config.RAW_TF_IN_GRAPH_ENV and virtual_resources
                        and isinstance(virtual_resources, list) and len(virtual_resources) > 0):
                    # We want to skip violations for raw TF resources and keep only virtual one's. The raw resource
                    # should have an array of attached virtual resources so we check it and skip if needed
                    continue
                if entity_context:
                    full_file_path = entity[CustomAttributes.FILE_PATH]
                    copy_of_check_result = pickle_deepcopy(check_result)
                    for skipped_check in entity_context.get("skipped_checks", []):
                        if skipped_check["id"] == check.id:
                            copy_of_check_result["result"] = CheckResult.SKIPPED
                            copy_of_check_result["suppress_comment"] = skipped_check["suppress_comment"]
                            break
                    copy_of_check_result["entity"] = entity[CustomAttributes.CONFIG]
                    connected_node_data = self._get_connected_node_data(entity.get(CustomAttributes.CONNECTED_NODE),  # type: ignore
                                                                        root_folder)
                    if platform.system() == "Windows":
                        root_folder = os.path.split(full_file_path)[0]
                    resource_id = ".".join(entity_context["definition_path"])
                    resource = resource_id
                    definition_context_file_path = full_file_path
                    if (
                        entity.get(CustomAttributes.TF_RESOURCE_ADDRESS)
                        and entity.get(CustomAttributes.TF_RESOURCE_ADDRESS) != resource_id
                    ):
                        # for plan resources
                        resource = entity[CustomAttributes.TF_RESOURCE_ADDRESS]
                    entity_config = self.get_graph_resource_entity_config(entity)
                    censored_code_lines = omit_secret_value_from_graph_checks(
                        check=check,
                        check_result=check_result,
                        entity_code_lines=entity_context.get("code_lines", []),
                        entity_config=entity_config,
                        resource_attributes_to_omit=runner_filter.resource_attr_to_omit,
                    )
                    record = Record(
                        check_id=check.id,
                        bc_check_id=check.bc_id,
                        check_name=check.name,
                        check_result=copy_of_check_result,
                        code_block=censored_code_lines,
                        file_path=f"{os.sep}{os.path.relpath(full_file_path, root_folder)}",
                        file_line_range=[
                            entity_context.get("start_line", 1),
                            entity_context.get("end_line", 1),
                        ],
                        resource=resource,
                        entity_tags=get_resource_tags(resource, entity_config),
                        evaluations=None,
                        check_class=check.__class__.__module__,
                        file_abs_path=os.path.abspath(full_file_path),
                        resource_address=entity_context.get("address"),
                        severity=check.severity,
                        bc_category=check.bc_category,
                        benchmarks=check.benchmarks,
                        connected_node=connected_node_data,
                        definition_context_file_path=definition_context_file_path,
                    )
                    if self.breadcrumbs:
                        breadcrumb = self.breadcrumbs.get(record.file_path, {}).get(resource)
                        if breadcrumb:
                            record = GraphRecord(record, breadcrumb)
                    record.set_guideline(check.guideline)
                    report.add_record(record=record)
        return report

    @abstractmethod
    def get_entity_context_and_evaluations(self, entity: dict[str, Any]) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def run_block(
        self,
        entities: list[dict[str, Any]],
        definition_context: _Context,
        full_file_path: _FilePath,
        root_folder: str,
        report: Report,
        scanned_file: str,
        block_type: str,
        runner_filter: RunnerFilter,
        entity_context_path_header: str | None = None,
        module_referrer: str | None = None,
    ) -> None:
        pass

    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None,
    ) -> list[Image]:
        if not graph_connector:
            # should not happen
            return []

        manager = TerraformImageReferencerManager(graph_connector=graph_connector)
        images = manager.extract_images_from_resources()

        return images

    @staticmethod
    def get_graph_resource_entity_config(entity: dict[str, Any]) -> dict[str, Any]:
        context_parser = parser_registry.context_parsers[entity[CustomAttributes.BLOCK_TYPE]]
        entity_config: dict[str, Any] = entity[CustomAttributes.CONFIG]
        definition_path = context_parser.get_entity_definition_path(entity_config)
        for path in definition_path:
            entity_config = entity_config[path]
        return entity_config
