from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from checkov.azure_pipelines.checks.registry import registry
from checkov.azure_pipelines.common.resource_id_utils import generate_resource_key_recursive
from checkov.azure_pipelines.image_referencer.manager import AzurePipelinesImageReferencerManager
from checkov.common.images.image_referencer import ImageReferencerMixin, Image
from checkov.common.output.report import CheckType, Report
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner


if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable
    from networkx import DiGraph


class Runner(ImageReferencerMixin["dict[str, dict[str, Any] | list[dict[str, Any]]]"], YamlRunner):
    check_type = CheckType.AZURE_PIPELINES  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f=f)
        return None

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        return file_path.endswith(('azure-pipelines.yml', 'azure-pipelines.yaml'))

    def get_resource(self, file_path: str, key: str, supported_entities: Iterable[str],
                     start_line: int = -1, end_line: int = -1, graph_resource: bool = False) -> str:
        if not self.definitions or not isinstance(self.definitions, dict):
            return key
        resource_name: Optional[str] = generate_resource_key_recursive(start_line, end_line, self.definitions[file_path])
        return resource_name if resource_name else key

    def run(
            self,
            root_folder: str | None = None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        report = super().run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                             files=files, runner_filter=runner_filter, collect_skip_comments=collect_skip_comments)
        if runner_filter.run_image_referencer:
            if files:
                # 'root_folder' shouldn't be empty to remove the whole path later and only leave the shortened form
                root_folder = os.path.split(os.path.commonprefix(files))[0]

            image_report = self.check_container_image_references(
                root_path=root_folder,
                runner_filter=runner_filter,
                definitions=self.definitions
            )

            if image_report:
                return [report, image_report]  # type:ignore[list-item]  # report can only be of type Report, not a list

        return report

    def extract_images(
            self,
            graph_connector: DiGraph | None = None,
            definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None,
            definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        images: list[Image] = []
        if not definitions:
            return images

        for file, config in definitions.items():
            if isinstance(config, list):
                continue
            is_container = False
            for row in self.definitions_raw.get(file, []):
                if 'container' in row[1]:
                    is_container = True
                    break
            if not is_container:
                return images
            manager = AzurePipelinesImageReferencerManager(workflow_config=config, file_path=file)
            images.extend(manager.extract_images_from_workflow())

        return images
