import logging
import os
from pathlib import Path
from typing import Optional, List, Tuple, Set, Union

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.vulnerability_scanning.package_scanner import SUPPORTED_PACKAGE_FILES
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import BaseRunner, ignored_directories, strtobool
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import create_report_record
from checkov.sca_package.scanner import Scanner


class Runner(BaseRunner):
    check_type = CheckType.SCA_PACKAGE

    def run(
        self,
        root_folder: Union[str, Path],
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True,
    ) -> Report:
        report = Report(self.check_type)

        if not strtobool(os.getenv("ENABLE_SCA_PACKAGE_SCAN", "False")):
            return report

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return report

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return report

        logging.info("SCA package scanning searching for scannable files")

        code_repo_path = Path(root_folder)

        excluded_paths = {*ignored_directories}
        if runner_filter.excluded_paths:
            excluded_paths.update(runner_filter.excluded_paths)

        input_output_paths = self.find_scannable_files(
            root_path=code_repo_path,
            files=files,
            excluded_paths=excluded_paths,
        )
        if not input_output_paths:
            # no packages found
            return report

        logging.info(f"SCA package scanning will scan {len(input_output_paths)} files")

        scanner = Scanner()
        scan_results = scanner.scan(input_output_paths)

        logging.info(f"SCA package scanning successfully scanned {len(scan_results)} files")

        for result in scan_results:
            package_file_path = Path(result["repository"])
            try:
                package_file_path = package_file_path.relative_to(code_repo_path)
            except ValueError:
                # Path.is_relative_to() was implemented in Python 3.9
                pass

            vulnerabilities = result.get("vulnerabilities") or []

            rootless_file_path = str(package_file_path).replace(package_file_path.anchor, "", 1)
            for vulnerability in vulnerabilities:
                record = create_report_record(
                    rootless_file_path=rootless_file_path,
                    file_abs_path=result["repository"],
                    check_class=f"{scanner.__module__}.{scanner.__class__.__qualname__}",
                    vulnerability_details=vulnerability,
                    runner_filter=runner_filter
                )
                if not runner_filter.should_run_check(record.check_id, record.bc_check_id):
                    if runner_filter.checks:
                        continue
                    else:
                        record.check_result = {
                            "result": CheckResult.SKIPPED,
                            "suppress_comment": f"{vulnerability['id']} is skipped"
                        }

                report.add_resource(record.resource)
                report.add_record(record)

        return report

    def find_scannable_files(
        self, root_path: Path, files: Optional[List[str]], excluded_paths: Set[str]
    ) -> Set[Tuple[Path, Path]]:
        input_paths = {
            file_path
            for file_path in root_path.glob("**/*")
            if file_path.name in SUPPORTED_PACKAGE_FILES and not any(p in file_path.parts for p in excluded_paths)
        }

        # filter out package.json, if package-lock.json exists
        package_lock_parent_paths = {
            file_path.parent for file_path in input_paths if file_path.name == "package-lock.json"
        }
        input_output_paths = {
            (file_path, file_path.parent / f"{file_path.stem}_result.json")
            for file_path in input_paths
            if file_path.name != "package.json" or file_path.parent not in package_lock_parent_paths
        }

        for file in files or []:
            file_path = Path(file)
            if not file_path.exists():
                logging.warning(f"File {file_path} doesn't exist")
                continue

            input_output_paths.add((file_path, file_path.parent / f"{file_path.stem}_result.json"))

        return input_output_paths
