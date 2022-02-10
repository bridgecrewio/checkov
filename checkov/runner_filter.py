import logging
import fnmatch
from collections.abc import Iterable
from typing import Set, Optional, Union, List

from checkov.common.bridgecrew.severities import Severity, Severities
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
            skip_cve_package: Optional[List] = None
    ) -> None:

        checks = convert_csv_string_arg_to_list(checks)
        skip_checks = convert_csv_string_arg_to_list(skip_checks)

        # we will store the lowest value severity we find in checks, and the highest value we find in skip-checks
        # so the logic is "run all checks >= severity" and/or "skip all checks <= severity"
        self.check_threshold = None
        self.skip_check_threshold = None
        self.checks = []
        self.skip_checks = []

        # split out check/skip thresholds so we can access them easily later
        for val in checks:
            if val in Severities:
                if not self.check_threshold or self.check_threshold.level > Severities[val].level:
                    self.check_threshold = Severities[val]
            else:
                self.checks.append(val)

        for val in skip_checks:
            if val in Severities:
                if not self.skip_check_threshold or self.skip_check_threshold.level < Severities[val].level:
                    self.skip_check_threshold = Severities[val]
            else:
                self.skip_checks.append(val)

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
        self.skip_cve_package = skip_cve_package


    def should_run_check(self, check=None, check_id=None, bc_check_id=None, severity=None) -> bool:
        if check:
            check_id = check.id
            bc_check_id = check.bc_id
            severity = check.bc_severity
        if RunnerFilter.is_external_check(check_id) and self.all_external:
            pass  # enabled unless skipped
        elif self.checks or self.check_threshold:
            if self.check_matches(check_id, bc_check_id, severity, self.checks, self.check_threshold, False):
                return True
            return False

        if (self.skip_checks or self.skip_check_threshold) and self.check_matches(check_id, bc_check_id, severity, self.skip_checks, self.skip_check_threshold, threshold_is_max=True):
            return False
        return True

    @staticmethod
    def check_matches(check_id: str,
                      bc_check_id: str,
                      severity: Optional[Severity],
                      pattern_list: List[str],
                      threshold: Optional[Severity] = None,
                      threshold_is_max: Optional[bool] = None):

        # if it matches the threshold, then we can just return the result. If it doesn't, then we will check specific
        # exclusions below
        if severity and threshold:
            if severity.level <= threshold.level and threshold_is_max:
                return True
            if severity.level >= threshold.level and not threshold_is_max:
                return True

        for pattern in pattern_list:
            if (
                    ((check_id and fnmatch.fnmatch(check_id, pattern))
                     or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern)))
            ):
                return True
        return False

    @staticmethod
    def notify_external_check(check_id: str) -> None:
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id: str) -> bool:
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
