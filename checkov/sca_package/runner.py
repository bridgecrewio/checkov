import logging
import os
from pathlib import Path
from typing import Optional, List, Tuple, Set, Union

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.vulnerability_scanning.package_scanner import SUPPORTED_PACKAGE_FILES
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, ignored_directories, strtobool
from checkov.common.typing import _CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import create_vulnerabilities_record
from checkov.sca_package.scanner import Scanner


class Runner(BaseRunner):
    check_type = "sca_package"

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
            vulnerability_dist = result["vulnerabilityDistribution"]

            check_result: _CheckResult = {
                "result": CheckResult.FAILED if vulnerabilities else CheckResult.PASSED,
            }

            rootless_file_path = str(package_file_path).replace(package_file_path.anchor, "", 1)
            report.add_resource(rootless_file_path)
            report.add_record(
                Record(
                    check_id="CKV_VUL_2",
                    bc_check_id="BC_VUL_2",
                    check_name="SCA package scan",
                    check_result=check_result,
                    code_block=[],
                    file_path=f"/{rootless_file_path}",
                    file_line_range=(0, 0),
                    resource=package_file_path.name,
                    check_class=f"{scanner.__module__}.{scanner.__class__.__qualname__}",
                    evaluations=None,
                    file_abs_path=result["repository"],
                    vulnerabilities=create_vulnerabilities_record(vulnerabilities, vulnerability_dist),
                )
            )

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
