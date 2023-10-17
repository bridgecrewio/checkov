from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, List

from checkov.common.bridgecrew.bc_source import IDEsSourceTypes
from checkov.common.sca.commons import should_run_scan
from checkov.common.sca.output import add_to_report_sca_data
from checkov.common.typing import _LicenseStatus
from checkov.common.bridgecrew.platform_integration import bc_integration, FileToPersist
from checkov.common.models.consts import SCANNABLE_PACKAGE_FILES_EXTENSIONS, SCANNABLE_PACKAGE_FILES
from checkov.common.models.enums import ErrorStatus
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner, ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.sca_package_2.scanner import Scanner


class Runner(BaseRunner[None, None, None]):
    check_type = CheckType.SCA_PACKAGE  # noqa: CCE003  # a static attribute

    def __init__(self, report_type: str = check_type) -> None:
        super().__init__(file_extensions=SCANNABLE_PACKAGE_FILES_EXTENSIONS, file_names=SCANNABLE_PACKAGE_FILES)
        self._check_class: str | None = None
        self._code_repo_path: Path | None = None
        self.report_type = report_type

    def prepare_and_scan(
            self,
            root_folder: str | Path | None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            excluded_file_names: set[str] | None = None,
    ) -> tuple[dict[str, Any] | None, list[FileToPersist]]:
        runner_filter = runner_filter or RunnerFilter()
        excluded_file_names = excluded_file_names or set()

        # skip complete run, if flag '--check' was used without a CVE check ID or the license policies
        if not should_run_scan(runner_filter.checks):
            return None, []

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return None, []

        if bc_integration.bc_source and bc_integration.bc_source.name in IDEsSourceTypes \
                and not bc_integration.is_prisma_integration():
            logging.info("The --bc-api-key flag needs to be set to a Prisma token for SCA scan for vscode or jetbrains extention")
            return {}, []  # should just return an empty result

        self._code_repo_path = Path(root_folder) if root_folder else None

        if not bc_integration.timestamp and bc_integration.bc_source and not bc_integration.bc_source.upload_results:
            bc_integration.set_s3_integration()

        excluded_paths = {*ignored_directories}
        if runner_filter.excluded_paths:
            excluded_paths.update(runner_filter.excluded_paths)

        uploaded_files: List[FileToPersist] | None = self.upload_package_files(
            root_path=self._code_repo_path,
            files=files,
            excluded_paths=excluded_paths,
            excluded_file_names=excluded_file_names,
        )
        if uploaded_files is None:
            # failure happened during uploading
            return None, []

        if len(uploaded_files) == 0:
            # no packages were uploaded. we can skip the scanning
            return {}, uploaded_files

        scanner = Scanner(self.pbar, root_folder)
        self._check_class = f"{scanner.__module__}.{scanner.__class__.__qualname__}"
        scan_results = scanner.scan()

        if scan_results is not None:
            logging.info(f"SCA package scanning successfully scanned {len(scan_results)} files")

        return scan_results, uploaded_files

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
        scan_results, uploaded_files = self.prepare_and_scan(root_folder, files, runner_filter)
        if scan_results is None:
            report.set_error_status(ErrorStatus.ERROR)
            return report

        for path, result in scan_results.items():
            if not result:
                continue
            bc_integration.source_id = result.get("sourceId")
            package_file_path = Path(path)
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
            inline_suppressions = result.get("inlineSuppressions")

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
                dependencies=result.get("dependencies", None),
                inline_suppressions=inline_suppressions,
                used_private_registry=result.get("used_private_reg", False)
            )

        return report

    def _persist_file_if_required(self, package_files_to_persist: List[FileToPersist],
                                  file_path: Path, root_path: Path | None) -> None:
        if file_path.name in SCANNABLE_PACKAGE_FILES or file_path.suffix in SCANNABLE_PACKAGE_FILES_EXTENSIONS:
            file_path_str = str(file_path)
            # in case of root_path is None, we will get the path in related to the current work dir
            package_files_to_persist.append(FileToPersist(file_path_str, os.path.relpath(file_path_str, root_path)))

    def upload_package_files(
            self,
            root_path: Path | None,
            files: list[str] | None,
            excluded_paths: set[str],
            excluded_file_names: set[str] | None = None,
    ) -> List[FileToPersist] | None:
        """ upload package files to s3"""
        logging.info("SCA package scanning upload for package files")
        excluded_file_names = excluded_file_names or set()
        package_files_to_persist: List[FileToPersist] = []
        try:
            if root_path:
                for file_path in root_path.glob("**/*"):
                    if any(p in file_path.parts for p in excluded_paths) or file_path.name in excluded_file_names:
                        logging.debug(f"[sca_package:runner](upload_package_files) - File {file_path} was excluded")
                        continue
                    self._persist_file_if_required(package_files_to_persist, file_path, root_path)

            if files:
                for file in files:
                    file_path = Path(file)
                    if not file_path.exists():
                        logging.warning(f"[sca_package:runner](upload_package_files) - File {file_path} doesn't exist")
                        continue
                    self._persist_file_if_required(package_files_to_persist, file_path, root_path)

            logging.info(f"{len(package_files_to_persist)} sca package files found.")
            bc_integration.persist_files(package_files_to_persist)
            return package_files_to_persist
        except Exception:
            logging.debug("Unexpected failure happened during uploading files for package scanning.\n"
                          "the scanning is terminating. details are below.\n"
                          "please try again. if it is repeated, please report.", exc_info=True)
            return None
