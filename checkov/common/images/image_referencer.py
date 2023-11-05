from __future__ import annotations

import asyncio
import logging
from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TYPE_CHECKING, Generic, TypeVar

import aiohttp
import docker

from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner
from checkov.common.bridgecrew.vulnerability_scanning.integrations.docker_image_scanning import \
    docker_image_scanning_integration
from checkov.common.output.common import ImageDetails
from checkov.common.output.report import Report, CheckType
from checkov.common.sca.commons import should_run_scan
from checkov.common.sca.output import add_to_report_sca_data, get_license_statuses_async
from checkov.common.typing import _LicenseStatus

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.runner_filter import RunnerFilter
    from networkx import DiGraph

_Definitions = TypeVar("_Definitions")

INVALID_IMAGE_NAME_CHARS = ("[", "{", "(", "<", "$")


def fix_related_resource_ids(report: Report | None, tmp_dir: str) -> None:
    """Remove tmp dir prefix from 'relatedResourceId'"""

    if report and report.image_cached_results:
        for cached_result in report.image_cached_results:
            related_resource_id = cached_result.get("relatedResourceId")
            if related_resource_id and isinstance(related_resource_id, str):
                cached_result["relatedResourceId"] = related_resource_id.replace(tmp_dir, "", 1)


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
                return image.short_id
            return image.short_id
        except Exception:
            logging.debug(f"failed to pull docker image={image_name}", exc_info=True)
            return ""


def is_valid_public_image_name(image_name: str) -> bool:
    if image_name.startswith('localhost'):
        return False
    if any(char in image_name for char in INVALID_IMAGE_NAME_CHARS):
        return False
    if image_name.count(":") > 1:
        # if there is more than one colon, then it is typically a private registry with port reference
        return False
    return True


class ImageReferencerMixin(Generic[_Definitions]):
    """Mixin class to simplify image reference search"""

    def check_container_image_references(
        self,
        root_path: str | Path | None,
        runner_filter: RunnerFilter,
        graph_connector: DiGraph | None = None,
        definitions: _Definitions | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None,
    ) -> Report | None:
        """Tries to find image references in graph based IaC templates"""
        from checkov.common.bridgecrew.platform_integration import bc_integration

        # skip complete run, if flag '--check' was used without a CVE check ID
        if not should_run_scan(runner_filter.checks):
            return None

        images = self.extract_images(graph_connector=graph_connector, definitions=definitions,
                                     definitions_raw=definitions_raw)
        if not images:
            return None

        logging.info(f"Found {len(images)} image references {[image.name for image in images]}")

        report = Report(CheckType.SCA_IMAGE)
        root_path = Path(root_path) if root_path else None
        check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        report_type = CheckType.SCA_IMAGE
        image_names_to_query = list(set(filter(lambda i: is_valid_public_image_name(i), map(lambda i: i.name, images))))
        results = asyncio.run(self._fetch_image_results_async(image_names_to_query))

        license_statuses_by_image = asyncio.run(self._fetch_licenses_per_image(image_names_to_query, results))

        for image in images:
            try:
                results_index = image_names_to_query.index(image.name)
                cached_results = results[results_index]
            except ValueError:
                cached_results = {}

            file_line_range = [image.start_line, image.end_line]
            self._add_image_records(
                report=report,
                root_path=root_path,
                check_class=check_class,
                dockerfile_path=image.file_path,
                image=image,
                runner_filter=runner_filter,
                report_type=report_type,
                bc_integration=bc_integration,
                cached_results=cached_results,
                license_statuses=license_statuses_by_image.get(image.name) or [],
                file_line_range=file_line_range if None not in file_line_range else None
            )

        return report

    @staticmethod
    async def _fetch_image_results_async(image_names_to_query: list[str]) -> list[dict[str, Any]]:
        """
        This is an async implementation of `_fetch_image_results`. The only change is we're getting a session
        as an input, and the asyncio behavior is managed in the calling method.
        """
        async with aiohttp.ClientSession() as session:
            results: list[dict[str, Any]] = await asyncio.gather(*[
                image_scanner.get_scan_results_from_cache_async(session, f"image:{i}")
                for i in image_names_to_query
            ])
        return results

    def _add_image_records(
        self,
        report: Report,
        root_path: Path | None,
        check_class: str,
        dockerfile_path: str,
        image: Image,
        runner_filter: RunnerFilter,
        report_type: str,
        bc_integration: BcPlatformIntegration,
        cached_results: dict[str, Any],
        license_statuses: list[_LicenseStatus],
        file_line_range: list[int] | None = None
    ) -> None:
        """Adds an image record to the given report, if possible"""
        if cached_results:
            logging.info(f"Found cached scan results of image {image.name}")
            image_scanning_report: dict[str, Any] = docker_image_scanning_integration.create_report(
                twistcli_scan_result=cached_results,
                bc_platform_integration=bc_integration,
                file_path=dockerfile_path,
                file_content=f'image: {image.name}',
                docker_image_name=image.name,
                related_resource_id=image.related_resource_id,
                root_folder=root_path,
                error_lines=file_line_range
            )
            report.image_cached_results.append(image_scanning_report)

            result = cached_results.get("results", [{}])[0]
            image_id = self._extract_image_short_id(result)
            image_details = self._get_image_details_from_twistcli_result(scan_result=result, image_id=image_id)
            dockerfile_rel_path = dockerfile_path
            if root_path:
                try:
                    dockerfile_rel_path = str(Path(dockerfile_path).relative_to(root_path))
                except ValueError:
                    # Path.is_relative_to() was implemented in Python 3.9
                    pass
            rootless_file_path = dockerfile_rel_path.replace(Path(dockerfile_rel_path).anchor, "", 1)
            rootless_file_path_to_report = f"{rootless_file_path} ({image.name} lines:{image.start_line}-" \
                                           f"{image.end_line} ({image_id}))"

            self._add_vulnerability_records(
                report=report,
                result=result,
                check_class=check_class,
                dockerfile_path=dockerfile_path,
                rootless_file_path=rootless_file_path_to_report,
                image_details=image_details,
                runner_filter=runner_filter,
                report_type=report_type,
                license_statuses=license_statuses,
                file_line_range=file_line_range
            )
        else:
            logging.info(f"No cache hit for image {image.name}")

    @staticmethod
    def _extract_image_short_id(scan_result: dict[str, Any]) -> str:
        """Extracts a shortened version of the image ID from the scan result"""

        if "id" not in scan_result:
            return "sha256:unknown"

        image_id: str = scan_result["id"]

        if image_id.startswith("sha256:"):
            return image_id[:17]
        return image_id[:10]

    @staticmethod
    def _get_image_details_from_twistcli_result(scan_result: dict[str, Any], image_id: str) -> ImageDetails:
        """Extracts the image detaisl from a twistcli scan result"""

        image_packages = scan_result.get("packages", [])
        image_package_types = {f'{package["name"]}@{package["version"]}': package["type"] for package in image_packages}
        return ImageDetails(
            distro=scan_result.get("distro", ""),
            distro_release=scan_result.get("distroRelease", ""),
            package_types=image_package_types,
            image_id=image_id,
        )

    @staticmethod
    def _add_vulnerability_records(
        report: Report,
        result: dict[str, Any],
        check_class: str,
        dockerfile_path: str,
        rootless_file_path: str,
        image_details: ImageDetails | None,
        license_statuses: list[_LicenseStatus],
        runner_filter: RunnerFilter,
        report_type: str,
        file_line_range: list[int] | None = None
    ) -> None:
        vulnerabilities = result.get("vulnerabilities", [])
        packages = result.get("packages", [])
        add_to_report_sca_data(
            report=report,
            check_class=check_class,
            scanned_file_path=dockerfile_path,
            rootless_file_path=rootless_file_path,
            runner_filter=runner_filter,
            vulnerabilities=vulnerabilities,
            packages=packages,
            license_statuses=license_statuses,
            sca_details=image_details,
            report_type=report_type,
            file_line_range=file_line_range
        )

    @abstractmethod
    def extract_images(
        self,
        graph_connector: DiGraph | None = None,
        definitions: _Definitions | None = None,
        definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        """Tries to find image references in the graph or supported resource"""

        pass

    @staticmethod
    async def _fetch_licenses_per_image(image_names: list[str], image_results: list[dict[str, Any]]) \
            -> dict[str, list[_LicenseStatus]]:
        merged_result: dict[str, list[_LicenseStatus]] = {}
        async with aiohttp.ClientSession() as session:
            license_results = await asyncio.gather(*[
                get_license_statuses_async(session, result['results'][0].get('packages') or [], image_names[i])
                for i, result in enumerate(image_results)
                if "results" in result and result["results"]
            ])
        merged_result.update({r['image_name']: r['licenses'] for r in license_results})
        return merged_result
