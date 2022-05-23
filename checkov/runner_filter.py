import logging
import fnmatch
from collections.abc import Iterable
from typing import Set, Optional, Union, List

from checkov.common.bridgecrew.severities import Severity, Severities
from checkov.common.checks.base_check import BaseCheck
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
            include_all_checkov_policies: bool = True,
            download_external_modules: bool = False,
            external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
            evaluate_variables: bool = True,
            runners: Optional[List[str]] = None,
            skip_framework: Optional[List[str]] = None,
            excluded_paths: Optional[List[str]] = None,
            all_external: bool = False,
            var_files: Optional[List[str]] = None,
            skip_cve_package: Optional[List[str]] = None
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
        for val in (checks or []):
            if val in Severities:
                if not self.check_threshold or self.check_threshold.level > Severities[val].level:
                    self.check_threshold = Severities[val]
            else:
                self.checks.append(val)

        for val in (skip_checks or []):
            if val in Severities:
                if not self.skip_check_threshold or self.skip_check_threshold.level < Severities[val].level:
                    self.skip_check_threshold = Severities[val]
            else:
                self.skip_checks.append(val)

        self.include_all_checkov_policies = include_all_checkov_policies

        self.framework: "Iterable[str]" = framework if framework else ["all"]
        if skip_framework:
            if "all" in self.framework:
                if runners is None:
                    runners = []

                self.framework = set(runners) - set(skip_framework)
            else:
                self.framework = set(self.framework) - set(skip_framework)
        logging.debug(f"Resultant set of frameworks (removing skipped frameworks): {','.join(self.framework)}")

        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.evaluate_variables = evaluate_variables
        self.excluded_paths = excluded_paths or []
        self.all_external = all_external
        self.var_files = var_files
        self.skip_cve_package = skip_cve_package

    def should_run_check(self,
                         check: Optional[BaseCheck] = None,
                         check_id: Optional[str] = None,
                         bc_check_id: Optional[str] = None,
                         severity: Optional[Severity] = None) -> bool:
        if check:
            check_id = check.id
            bc_check_id = check.bc_id
            severity = check.severity

        assert check_id is not None  # nosec (for mypy (and then for bandit))

        run_severity = severity and self.check_threshold and severity.level >= self.check_threshold.level
        explicit_run = self.checks and self.check_matches(check_id, bc_check_id, self.checks)
        implicit_run = not self.checks and not self.check_threshold
        is_external = RunnerFilter.is_external_check(check_id)

        # True if this check is present in the allow list, or if there is no allow list
        # this is not necessarily the return value (need to apply other filters)
        should_run_check = (
            run_severity or
            explicit_run or
            implicit_run or
            (is_external and self.all_external)
        )

        if not should_run_check:
            return False

        skip_severity = severity and self.skip_check_threshold and severity.level <= self.skip_check_threshold.level
        explicit_skip = self.skip_checks and self.check_matches(check_id, bc_check_id, self.skip_checks)

        should_skip_check = (
            skip_severity or
            explicit_skip or
            (not bc_check_id and not self.include_all_checkov_policies and not is_external and not explicit_run)
        )

        if should_skip_check:
            result = False
        elif should_run_check:
            result = True
        else:
            result = False

        logging.debug(f'Should run check {check_id}: {result}')
        return result

    @staticmethod
    def check_matches(check_id: str,
                      bc_check_id: Optional[str],
                      pattern_list: List[str]) -> bool:
        return any(
            (fnmatch.fnmatch(check_id, pattern) or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern))) for pattern
            in pattern_list)

    def within_threshold(self, severity: Severity) -> bool:
        above_min = (not self.check_threshold) or self.check_threshold.level <= severity.level
        below_max = self.skip_check_threshold and self.skip_check_threshold.level >= severity.level
        return above_min and not below_max

    @staticmethod
    def notify_external_check(check_id: str) -> None:
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id: str) -> bool:
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
