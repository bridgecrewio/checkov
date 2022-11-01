from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.circleci_pipelines.image_referencer.manager import CircleCIImageReferencerManager
from checkov.common.images.image_referencer import Image, ImageReferencerMixin
from checkov.common.output.report import CheckType, Report
from checkov.circleci_pipelines.registry import registry
from checkov.common.util.type_forcers import force_dict
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from networkx import DiGraph

WORKFLOW_DIRECTORY = "circleci"


class Runner(ImageReferencerMixin["dict[str, dict[str, Any] | list[dict[str, Any]]]"], YamlRunner):
    check_type = CheckType.CIRCLECI_PIPELINES  # noqa: CCE003  # a static attribute

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def included_paths(self) -> list[str]:
        return [".circleci"]

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if self.is_workflow_file(f):
            return super()._parse_file(f)

        return None

    def is_workflow_file(self, file_path: str) -> bool:
        """
        :return: True if the file mentioned is named config.yml/yaml in .circleci dir from included_paths(). Otherwise: False
        """
        abspath = os.path.abspath(file_path)
        return WORKFLOW_DIRECTORY in abspath and abspath.endswith(("config.yml", "config.yaml"))

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

        for file_path, config in definitions.items():
            _config = force_dict(config) or {}
            if not config:
                continue
            manager = CircleCIImageReferencerManager(workflow_config=_config, file_path=file_path)
            images.extend(manager.extract_images_from_workflow())

        return images
