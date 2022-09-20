from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.common.output.report import Report

from checkov.runner_filter import RunnerFilter
from networkx import DiGraph

from checkov.common.images.image_referencer import Image, ImageReferencerMixin
from checkov.common.bridgecrew.check_type import CheckType
from checkov.gitlab_ci.checks.registry import registry
from checkov.gitlab_ci.image_referencer.manager import GitlabCiImageReferencerManager
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from collections.abc import Iterable


class Runner(ImageReferencerMixin, YamlRunner):
    check_type = CheckType.GITLAB_CI  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()
        self.workflow_config: dict[str, Any] = {}
        self.file_path = ''

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    def _parse_file(
        self, f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        self.file_path = f
        if self.is_workflow_file(f):
            parsed_file = super()._parse_file(f=f, file_content=file_content)
            if not parsed_file:
                return None
            config, config_line_numbers = parsed_file
            self.workflow_config = config
            return config, config_line_numbers

        return None

    def is_workflow_file(self, file_path: str) -> bool:
        """
        :return: True if the file mentioned is in the gitlab workflow name .gitlab-ci.yml. Otherwise: False
        """
        return file_path.endswith((".gitlab-ci.yml", ".gitlab-ci.yaml"))

    def included_paths(self) -> Iterable[str]:
        return (".gitlab-ci.yml", ".gitlab-ci.yaml")

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
                graph_connector=None,
                root_path=root_folder,
                runner_filter=runner_filter
            )

            if image_report:
                return [report, image_report]

        return report

    def extract_images(
        self, graph_connector: DiGraph | None = None, resources: list[dict[str, Any]] | None = None
    ) -> list[Image]:
        manager = GitlabCiImageReferencerManager(supported_keys=("image", "services"),
                                                 workflow_config=self.workflow_config,
                                                 file_path=self.file_path)
        images: list[Image] = manager.extract_images_from_workflow()

        return images
