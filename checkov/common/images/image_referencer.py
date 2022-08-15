from __future__ import annotations

import logging
import os
from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import cast, Any, TYPE_CHECKING

import docker

from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.output.common import ImageDetails
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import strtobool
from checkov.common.sca.output import parse_vulns_to_records

if TYPE_CHECKING:
    from checkov.runner_filter import RunnerFilter
    from networkx import DiGraph


class Image:
    def __init__(self, file_path: str, name: str, start_line: int, end_line: int,
                 related_resource_id: str | None = None) -> None:
        """

        :param file_path: example: 'checkov/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml'
        :param name: example: 'node:14.16'
        :param image_id: example: 'sha256:6a353e22ce'
        :param start_line: example: 8
        :param end_line: example: 16
        """
        self.end_line = end_line
        self.start_line = start_line
        self.name = name
        self.file_path = file_path
        self.related_resource_id = related_resource_id

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.file_path, self.name, self.start_line, self.end_line))


class ImageReferencer:
    @abstractmethod
    def is_workflow_file(self, file_path: str) -> bool:
        """

        :param file_path: path of file to validate if it is a file that contains might images (example: CI workflow file)
        :return: True if contains images

        """
        return False

    @abstractmethod
    def get_images(self, file_path: str) -> Iterable[Image]:
        """
        Get container images mentioned in a file
        :param file_path: File to be inspected
        :return: List of container images objects mentioned in the file.
        """
        return []

    @staticmethod
    def inspect(image_name: str) -> str:
        """

        :param image_name: name of the image to be inspected locally using a "docker inspect X". If image does not exist try to pull it locally.
        :return: short image id sha that is inspected. In case inspect has failed None will be returned.
        """
        try:
            logging.info("Inspecting docker image {}".format(image_name))
            client = docker.from_env()
            try:
                image = client.images.get(image_name)
            except Exception:
                image = client.images.pull(image_name)
                return cast(str, image.short_id)
            return cast(str, image.short_id)
        except Exception:
            logging.debug(f"failed to pull docker image={image_name}", exc_info=True)
            return ""


class ImageReferencerMixin:
    """Mixin class to simplify image reference search"""

    def check_container_image_references(
        self,
        graph_connector: DiGraph,
        root_path: str | Path | None,
        runner_filter: RunnerFilter,
        supported_resource_types: Iterable[str],
    ) -> Report | None:
        """Tries to find image references in graph based IaC templates"""

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return None

        resources = [
            block
            for node, block in graph_connector.nodes(data=True)
            if block and block.get(CustomAttributes.RESOURCE_TYPE) in supported_resource_types
        ]
        if not resources:
            return None

        images = self.extract_images(resources=resources)
        if not images:
            return None

        logging.info(f"Found {len(images)} image references {[image.name for image in images]}")

        report = Report(CheckType.SCA_IMAGE)
        root_path = Path(root_path) if root_path else None
        check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        report_type = CheckType.SCA_IMAGE

        for image in images:
            self.add_image_records(
                report=report,
                root_path=root_path,
                check_class=check_class,
                dockerfile_path=image.file_path,
                image=image,
                runner_filter=runner_filter,
                report_type=report_type,
            )

        return report

    def add_image_records(
        self,
        report: Report,
        root_path: Path | None,
        check_class: str,
        dockerfile_path: str,
        image: Image,
        runner_filter: RunnerFilter,
        report_type: str,
    ) -> None:
        """Adds an image record to the given report, if possible"""

        cached_results: dict[str, Any] = image_scanner.get_scan_results_from_cache(f"image:{image.name}")
        if cached_results:
            logging.info(f"Found cached scan results of image {image.name}")

            result = cached_results.get("results", [{}])[0]
            vulnerabilities = result.get("vulnerabilities") or []
            image_id = self.extract_image_short_id(result)
            image_details = self.get_image_details_from_twistcli_result(scan_result=result, image_id=image_id)
            if root_path:
                try:
                    dockerfile_path = str(Path(dockerfile_path).relative_to(root_path))
                except ValueError:
                    # Path.is_relative_to() was implemented in Python 3.9
                    pass
            rootless_file_path = dockerfile_path.replace(Path(dockerfile_path).anchor, "", 1)

            parse_vulns_to_records(
                report=report,
                check_class=check_class,
                scanned_file_path=os.path.abspath(dockerfile_path),
                rootless_file_path=f"{rootless_file_path} ({image.name} lines:{image.start_line}-{image.end_line} ({image_id}))",
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=[],
                license_statuses=[],
                image_details=image_details,
                report_type=report_type,
            )
        elif strtobool(os.getenv("CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING", "False")):
            # experimental flag on running image referencers via local twistcli
            from checkov.sca_image.runner import Runner as sca_image_runner

            runner = sca_image_runner()

            image_id = ImageReferencer.inspect(image.name)
            scan_result = runner.scan(image_id, dockerfile_path, runner_filter)
            if scan_result is None:
                return None

            self.raw_report = scan_result
            result = scan_result.get('results', [{}])[0]
            vulnerabilities = result.get("vulnerabilities") or []
            parse_vulns_to_records(
                report=report,
                check_class=check_class,
                scanned_file_path=os.path.abspath(dockerfile_path),
                rootless_file_path=f"{dockerfile_path} ({image.name} lines:{image.start_line}-{image.end_line} ({image_id}))",
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=[],
                license_statuses=[],
            )
        else:
            logging.info(f"No cache hit for image {image.name}")

    def extract_image_short_id(self, scan_result: dict[str, Any]) -> str:
        """Extracts a shortened version of the image ID from the scan result"""

        if "id" not in scan_result:
            return "sha256:unknown"

        image_id: str = scan_result["id"]

        if image_id.startswith("sha256:"):
            return image_id[:17]
        return image_id[:10]

    def get_image_details_from_twistcli_result(self, scan_result: dict[str, Any], image_id: str) -> ImageDetails:
        """Extracts the image detaisl from a twistcli scan result"""

        image_packages = scan_result.get("packages", [])
        image_package_types = {f'{package["name"]}@{package["version"]}': package["type"] for package in image_packages}
        return ImageDetails(
            distro=scan_result.get("distro", ""),
            distro_release=scan_result.get("distroRelease", ""),
            package_types=image_package_types,
            image_id=image_id,
        )

    @abstractmethod
    def extract_images(self, resources: list[dict[str, Any]]) -> list[Image]:
        """Tries to find image references in supported resource types"""

        pass
