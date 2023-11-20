from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import jmespath

from checkov.bitbucket_pipelines.registry import registry
from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.bridgecrew.check_type import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Runner(YamlRunner, ImageReferencer):
    check_type = CheckType.BITBUCKET_PIPELINES  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def require_external_checks(self) -> bool:
        return False

    def import_registry(self) -> BaseCheckRegistry:
        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        if Runner.is_workflow_file(f):
            return YamlRunner._parse_file(f)

        return None

    @staticmethod
    def is_workflow_file(file_path: str) -> bool:
        """
        :return: True if the file mentioned is named bitbucket-pipelines.yml. Otherwise: False
        """
        return file_path.endswith(("bitbucket-pipelines.yml", "bitbucket-pipelines.yaml"))

    def get_images(self, file_path: str) -> set[Image]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected

        File sample that will return 4 Image objects:
        #image: node:10.15.0
        #
        #pipelines:
        #  default:
        #    - step:
        #        name: Build and test
        #        image: node:10.0.0
        #        script:
        #          - npm install
        #          - npm test
        #          - npm run build
        #        artifacts:
        #          - dist/**
        #    - step:
        #        name: Deploy
        #        image: python:3.7.2
        #        trigger: manual
        #        script:
        #          - python deploy.py
        #  custom:
        #    sonar:
        #      - step:
        #          image: python:3.8.2
        #          script:
        #            - echo "Manual triggers for Sonar are awesome!"
        #    deployment-to-prod:
        #      - step:
        #          script:
        #            - echo "Manual triggers for deployments are awesome!"
        #  branches:
        #    staging:
        #      - step:
        #          script:
        #            - echo "Auto pipelines are cool too."
        :return: List of container image objects mentioned in the file.

        """

        images: set[Image] = set()
        parsed_file = self._parse_file(file_path)

        if not parsed_file:
            return images

        workflow, workflow_line_numbers = parsed_file

        if not isinstance(workflow, dict):
            # make type checking happy
            return images

        self.add_default_and_pipelines_images(workflow, images, file_path)
        self.add_root_image(file_path, images, workflow_line_numbers, workflow)

        return images

    def add_default_and_pipelines_images(self, workflow: dict[str, Any], images: set[Image], file_path: str) -> None:
        """

        :param workflow: parsed workflow file
        :param images: set of images to be updated
        :param file_path: path of analyzed workflow
        """
        keywords = [
            "pipelines.default[].step.{image: image, __startline__: __startline__, __endline__:__endline__}",
            "pipelines.*.[*][][][].step.{image: image, __startline__: __startline__, __endline__:__endline__}",
        ]
        for keyword in keywords:
            results = cast("list[dict[str, Any]]", jmespath.search(keyword, workflow))
            for result in results:
                image_name = result.get("image", None)
                if image_name:
                    image_obj = Image(
                        file_path=file_path,
                        name=image_name,
                        start_line=result["__startline__"],
                        end_line=result["__endline__"],
                    )
                    images.add(image_obj)

    def add_root_image(
        self, file_path: str, images: set[Image], workflow_line_numbers: list[tuple[int, str]], workflow: dict[str, Any]
    ) -> None:
        root_image = workflow.get("image", "")

        if root_image:
            for line_number, line_txt in workflow_line_numbers:
                if "image" in line_txt and not line_txt.startswith(" "):
                    image_obj = Image(
                        file_path=file_path,
                        name=root_image,
                        start_line=line_number,
                        end_line=line_number,
                    )
                    images.add(image_obj)
