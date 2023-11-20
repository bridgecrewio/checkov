from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import CheckType
from checkov.common.util.file_utils import read_file_with_any_encoding
from checkov.yaml_doc.runner import Runner as YamlRunner

# Import of the checks registry for a specific resource type
from checkov.argo_workflows.checks.registry import registry as template_registry

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry

API_VERSION_PATTERN = re.compile(r"^apiVersion:\s*argoproj.io/", re.MULTILINE)
KIND_PATTERN = re.compile(r"^kind:\s*Workflow", re.MULTILINE)


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.ARGO_WORKFLOWS  # noqa: CCE003  # a static attribute

    block_type_registries = {  # noqa: CCE003  # a static attribute
        "template": template_registry,
    }

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return self.block_type_registries["template"]

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        content = Runner._get_workflow_file_content(file_path=f)
        if content:
            return YamlRunner._parse_file(f=f, file_content=content)

        return None

    @staticmethod
    def _get_workflow_file_content(file_path: str) -> str | None:
        if not file_path.endswith((".yaml", ".yml")):
            return None

        content = read_file_with_any_encoding(file_path=file_path)
        if "argoproj.io" not in content:
            # the following regex will search more precisely, but no need to further process
            return None

        match_api = re.search(API_VERSION_PATTERN, content)
        if match_api:
            match_kind = re.search(KIND_PATTERN, content)
            if match_kind:
                # only scan Argo Workflows
                return content

        return None

    def is_workflow_file(self, file_path: str) -> bool:
        return self._get_workflow_file_content(file_path=file_path) is not None

    def get_images(self, file_path: str) -> set[Image]:
        """Get container images mentioned in a file

        Argo Workflows file can have a job and services run within a container.

        in the following sample file we can see a node:14.16 image:

        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
          generateName: template-defaults-
        spec:
          entrypoint: main
          templates:
            - name: main
              steps:
                - - name: retry-backoff
                    template: retry-backoff
                - - name: whalesay
                    template: whalesay

            - name: whalesay
              container:
                image: argoproj/argosay:v2
                command: [cowsay]
                args: ["hello world"]

            - name: retry-backoff
              container:
                image: python:alpine3.6
                command: ["python", -c]
                # fail with a 66% probability
                args: ["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"]

        Source: https://github.com/argoproj/argo-workflows/blob/master/examples/template-defaults.yaml

        :return: List of container image short ids mentioned in the file.
        Example return value for a file with node:14.16 image: ['sha256:6a353e22ce']
        """

        images: set[Image] = set()
        parsed_file = self._parse_file(file_path)

        if not parsed_file:
            return images

        workflow, workflow_line_numbers = parsed_file

        if not isinstance(workflow, dict):
            # make type checking happy
            return images

        spec = workflow.get("spec")
        if spec:
            templates = spec.get("templates")
            if isinstance(templates, list):
                for template in templates:
                    container = template.get("container")
                    if container:
                        image = self.extract_image(file_path=file_path, container=container)
                        if image:
                            images.add(image)
                    script = template.get("script")
                    if script:
                        image = self.extract_image(file_path=file_path, container=script)
                        if image:
                            images.add(image)

        return images

    def extract_image(self, file_path: str, container: dict[str, Any]) -> Image | None:
        image_name = container.get("image")
        if image_name and isinstance(image_name, str):
            start_line = container.get("__startline__", 0)
            end_line = container.get("__endline__", 0)
            return Image(
                file_path=file_path,
                name=image_name,
                start_line=start_line,
                end_line=end_line,
            )

        return None
