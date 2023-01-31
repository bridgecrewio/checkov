from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence, Any

from checkov.common.sca.commons import should_run_scan
from checkov.common.sca.output import add_to_report_sca_data
from checkov.common.typing import _LicenseStatus
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.consts import SUPPORTED_PACKAGE_FILES
from checkov.common.models.enums import ErrorStatus
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner, ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.scanner import Scanner


class Runner(BaseRunner[None]):
    check_type = CheckType.SCA_PACKAGE  # noqa: CCE003  # a static attribute

    def __init__(self, report_type: str = check_type) -> None:
        super().__init__(file_names=SUPPORTED_PACKAGE_FILES)
        self._check_class: str | None = None
        self._code_repo_path: Path | None = None
        self.report_type = report_type

    def prepare_and_scan(
            self,
            root_folder: str | Path | None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            exclude_package_json: bool = True,
            excluded_file_names: set[str] | None = None,
    ) -> Sequence[dict[str, Any]] | None:
        runner_filter = runner_filter or RunnerFilter()
        excluded_file_names = excluded_file_names or set()

        # skip complete run, if flag '--check' was used without a CVE check ID or the license policies
        if not should_run_scan(runner_filter.checks):
            return []

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return []

        logging.info("SCA package scanning searching for scannable files")

        self._code_repo_path = Path(root_folder) if root_folder else None

        excluded_paths = {*ignored_directories}
        if runner_filter.excluded_paths:
            excluded_paths.update(runner_filter.excluded_paths)

        input_paths = self.find_scannable_files(
            root_path=self._code_repo_path,
            files=files,
            excluded_paths=excluded_paths,
            exclude_package_json=exclude_package_json,
            excluded_file_names=excluded_file_names
        )
        if not input_paths:
            # no packages found
            return []

        logging.info(f"SCA package scanning will scan {len(input_paths)} files")

        scanner = Scanner(self.pbar, root_folder)
        self._check_class = f"{scanner.__module__}.{scanner.__class__.__qualname__}"

        # it will be None in case of unexpected failure during the scanning
        scan_results: Sequence[dict[str, Any]] | None = scanner.scan(input_paths)
        if scan_results is not None:
            logging.info(f"SCA package scanning successfully scanned {len(scan_results)} files")
        return scan_results

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

        report = Report(self.check_type)

        scan_results = self.prepare_and_scan(root_folder, files, runner_filter)
        if scan_results is None:
            report.set_error_status(ErrorStatus.ERROR)
            return report

        for result in scan_results:
            if not result:
                continue
            package_file_path = Path(result["repository"])
            if self._code_repo_path:
                try:
                    package_file_path = package_file_path.relative_to(self._code_repo_path)
                except ValueError:
                    # Path.is_relative_to() was implemented in Python 3.9
                    pass

            vulnerabilities = result.get("vulnerabilities") or []
            packages = result.get("packages") or []

            license_statuses = [_LicenseStatus(package_name=elm["packageName"], package_version=elm["packageVersion"],
                                               policy=elm["policy"], license=elm["license"], status=elm["status"])
                                for elm in result.get("license_statuses") or []]

            rootless_file_path = str(package_file_path).replace(package_file_path.anchor, "", 1)
            add_to_report_sca_data(
                report=report,
                check_class=self._check_class,
                scanned_file_path=str(package_file_path),
                rootless_file_path=rootless_file_path,
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=packages,
                license_statuses=license_statuses,
                report_type=self.report_type,
                dependencies=result.get("dependencies", None)
            )

        return report

    def find_scannable_files(
        self,
        root_path: Path | None,
        files: list[str] | None,
        excluded_paths: set[str],
        exclude_package_json: bool = True,
        excluded_file_names: set[str] | None = None,
        extra_supported_package_files: set[str] | None = None
    ) -> set[Path]:
        excluded_file_names = excluded_file_names or set()
        extra_supported_package_files = extra_supported_package_files or set()
        input_paths: set[Path] = set()
        if root_path:
            input_paths = {
                file_path
                for file_path in root_path.glob("**/*")
                if file_path.name in SUPPORTED_PACKAGE_FILES.union(extra_supported_package_files) and not any(p in file_path.parts for p in excluded_paths)
            }

            package_json_lock_parent_paths = set()
            if exclude_package_json:
                # filter out package.json, if package-lock.json or yarn.lock exists
                package_json_lock_parent_paths = {
                    file_path.parent for file_path in input_paths if
                    file_path.name in {"package-lock.json", "yarn.lock"}
                }

            input_paths = {
                file_path
                for file_path in input_paths
                if (file_path.name != "package.json" or file_path.parent not in package_json_lock_parent_paths) and file_path.name not in excluded_file_names
            }

        for file in files or []:
            file_path = Path(file)
            if not file_path.exists():
                logging.warning(f"File {file_path} doesn't exist")
                continue

            input_paths.add(file_path)

        return input_paths
