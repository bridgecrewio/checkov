from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence, Any
from collections import defaultdict

from checkov.common.typing import _LicenseStatus
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.consts import SUPPORTED_PACKAGE_FILES
from checkov.common.models.enums import CheckResult
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import BaseRunner, ignored_directories
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import create_report_cve_record, create_report_license_record
from checkov.sca_package.scanner import Scanner
from checkov.sca_package.commons import get_resource_for_record, get_file_path_for_record, get_package_alias


class Runner(BaseRunner):
    check_type = CheckType.SCA_PACKAGE  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(file_names=SUPPORTED_PACKAGE_FILES)
        self._check_class: str | None = None
        self._code_repo_path: Path | None = None

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

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return None

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return None

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
            return None

        logging.info(f"SCA package scanning will scan {len(input_paths)} files")

        scanner = Scanner(self.pbar, root_folder)
        self._check_class = f"{scanner.__module__}.{scanner.__class__.__qualname__}"
        scan_results = scanner.scan(input_paths)

        logging.info(f"SCA package scanning successfully scanned {len(scan_results)} files")
        return scan_results

    def run(
            self,
            root_folder: str | Path,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)

        scan_results = self.prepare_and_scan(root_folder, files, runner_filter)
        if scan_results is None:
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
            self.parse_vulns_to_records(
                report=report,
                scanned_file_path=str(package_file_path),
                rootless_file_path=rootless_file_path,
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=packages,
                license_statuses=license_statuses,
            )

        return report

    def parse_vulns_to_records(
        self,
        report: Report,
        scanned_file_path: str,
        rootless_file_path: str,
        runner_filter: RunnerFilter,
        vulnerabilities: list[dict[str, Any]],
        packages: list[dict[str, Any]],
        license_statuses: list[_LicenseStatus],
    ) -> None:
        licenses_per_package_map: dict[str, list[str]] = defaultdict(list)

        for license_status in license_statuses:
            # filling 'licenses_per_package_map', will be used in the call to 'create_report_cve_record' for efficient
            # extracting of license per package
            package_name, package_version, license = license_status["package_name"], license_status["package_version"], license_status["license"]
            licenses_per_package_map[get_package_alias(package_name, package_version)].append(license)

            license_record = create_report_license_record(
                rootless_file_path=rootless_file_path,
                file_abs_path=scanned_file_path,
                check_class=self._check_class,
                licenses_status=license_status
            )
            report.add_record(license_record)

        vulnerable_packages = []
        for vulnerability in vulnerabilities:
            package_name, package_version = vulnerability["packageName"], vulnerability["packageVersion"]
            cve_record = create_report_cve_record(
                rootless_file_path=rootless_file_path,
                file_abs_path=scanned_file_path,
                check_class=self._check_class,
                vulnerability_details=vulnerability,
                licenses=', '.join(licenses_per_package_map[get_package_alias(package_name, package_version)]) or 'Unknown',
                runner_filter=runner_filter
            )
            if not runner_filter.should_run_check(check_id=cve_record.check_id, bc_check_id=cve_record.bc_check_id,
                                                  severity=cve_record.severity):
                if runner_filter.checks:
                    continue
                else:
                    cve_record.check_result = {
                        "result": CheckResult.SKIPPED,
                        "suppress_comment": f"{vulnerability['id']} is skipped"
                    }

            report.add_resource(cve_record.resource)
            report.add_record(cve_record)
            vulnerable_packages.append(get_package_alias(package_name, package_version))

        for package in packages:
            if get_package_alias(package["name"], package["version"]) not in vulnerable_packages:
                # adding resources without cves for adding them also in the output-bom-repors
                report.extra_resources.add(
                    ExtraResource(
                        file_abs_path=scanned_file_path,
                        file_path=get_file_path_for_record(rootless_file_path),
                        resource=get_resource_for_record(rootless_file_path, package["name"]),
                        vulnerability_details={
                            "package_name": package["name"],
                            "package_version": package["version"],
                        }
                    )
                )

    def find_scannable_files(
        self,
        root_path: Path | None,
        files: list[str] | None,
        excluded_paths: set[str],
        exclude_package_json: bool = True,
        excluded_file_names: set[str] | None = None
    ) -> set[Path]:
        excluded_file_names = excluded_file_names or set()
        input_paths: set[Path] = set()
        if root_path:
            input_paths = {
                file_path
                for file_path in root_path.glob("**/*")
                if file_path.name in SUPPORTED_PACKAGE_FILES and not any(p in file_path.parts for p in excluded_paths)
            }

            package_lock_parent_paths = set()
            if exclude_package_json:
                # filter out package.json, if package-lock.json exists
                package_lock_parent_paths = {
                    file_path.parent for file_path in input_paths if file_path.name == "package-lock.json"
                }

            input_paths = {
                file_path
                for file_path in input_paths
                if (file_path.name != "package.json" or file_path.parent not in package_lock_parent_paths) and file_path.name not in excluded_file_names
            }

        for file in files or []:
            file_path = Path(file)
            if not file_path.exists():
                logging.warning(f"File {file_path} doesn't exist")
                continue

            input_paths.add(file_path)

        return input_paths
