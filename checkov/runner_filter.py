import logging
import fnmatch
from collections.abc import Iterable
from typing import Set, Optional, Union, List

from checkov.common.models.enums import Severities
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list


class RunnerFilter(object):
    # NOTE: This needs to be static because different filters may be used at load time versus runtime
    #       (see note in BaseCheckRegistery.register). The concept of which checks are external is
    #       logically a "static" concept anyway, so this makes logical sense.
    __EXTERNAL_CHECK_IDS: Set[str] = set()

    def __init__(
            self,
            framework: Optional[List[str]] = None,
            checks: Union[str, List[str], None] = None,
            skip_checks: Union[str, List[str], None] = None,
            download_external_modules: bool = False,
            external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
            evaluate_variables: bool = True,
            runners: Optional[List[str]] = None,
            skip_framework: Optional[List[str]] = None,
            excluded_paths: Optional[List[str]] = None,
            all_external: bool = False,
            var_files: Optional[List[str]] = None,
            min_cve_severity: str = 'none',
            skip_cve_package: Optional[List] = None
    ) -> None:

        self.checks = convert_csv_string_arg_to_list(checks)
        self.skip_checks = convert_csv_string_arg_to_list(skip_checks)

        self.framework: "Iterable[str]" = framework if framework else ["all"]
        if skip_framework:
            if "all" in self.framework:
                if runners is None:
                    runners = []

                self.framework = set(runners) - set(skip_framework)
            else:
                self.framework = set(self.framework) - set(skip_framework)
        logging.info(f"Resultant set of frameworks (removing skipped frameworks): {','.join(self.framework)}")

        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.evaluate_variables = evaluate_variables
        self.excluded_paths = excluded_paths
        self.all_external = all_external
        self.var_files = var_files
        self.min_cve_severity = min_cve_severity
        self.skip_cve_package = skip_cve_package

    def should_run_check(self, check=None, check_id=None, bc_check_id=None, severity=None) -> bool:
        if check:
            check_id = check.id
            bc_check_id = check.bc_id
            severity = check.bc_severity
        if RunnerFilter.is_external_check(check_id) and self.all_external:
            pass  # enabled unless skipped
        elif self.checks:
            if self.check_matches(check_id, bc_check_id, severity, self.checks):
                return True
            return False

        if self.skip_checks and self.check_matches(check_id, bc_check_id, severity, self.skip_checks):
            return False
        return True

    @staticmethod
    def check_matches(check_id: str, bc_check_id: str, severity: Optional[Severities], pattern_list: List[str]):
        for pattern in pattern_list:
            if (
                    ((check_id and fnmatch.fnmatch(check_id, pattern))
                     or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern)))
                    or (severity and severity.name == pattern)
            ):
                return True
        return False

    @staticmethod
    def notify_external_check(check_id: str) -> None:
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id: str) -> bool:
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
