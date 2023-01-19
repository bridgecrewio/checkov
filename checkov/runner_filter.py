from __future__ import annotations

import logging
import fnmatch
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Set, Optional, Union, List, TYPE_CHECKING, Dict, DefaultDict
import re

from checkov.secrets.consts import ValidationStatus

from checkov.common.bridgecrew.code_categories import CodeCategoryMapping, CodeCategoryConfiguration
from checkov.common.bridgecrew.severities import Severity, Severities
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck


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
            skip_cve_package: Optional[List[str]] = None,
            use_enforcement_rules: bool = False,
            filtered_policy_ids: Optional[List[str]] = None,
            show_progress_bar: Optional[bool] = True,
            run_image_referencer: bool = False,
            enable_secret_scan_all_files: bool = False,
            block_list_secret_scan: Optional[List[str]] = None,
            deep_analysis: bool = False,
            repo_root_for_plan_enrichment: Optional[List[str]] = None,
            resource_attr_to_omit: Optional[Dict[str, Set[str]]] = None
    ) -> None:

        checks = convert_csv_string_arg_to_list(checks)
        skip_checks = convert_csv_string_arg_to_list(skip_checks)

        self.skip_invalid_secrets = skip_checks and any(skip_check.capitalize() == ValidationStatus.INVALID.value
                                                        for skip_check in skip_checks)

        self.use_enforcement_rules = use_enforcement_rules
        self.enforcement_rule_configs: Optional[Dict[str, Severity]] = None

        # we will store the lowest value severity we find in checks, and the highest value we find in skip-checks
        # so the logic is "run all checks >= severity" and/or "skip all checks <= severity"
        self.check_threshold = None
        self.skip_check_threshold = None
        self.checks = []
        self.bc_cloned_checks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.skip_checks = []
        self.skip_checks_regex_patterns = defaultdict(lambda: [])
        self.show_progress_bar = show_progress_bar

        # split out check/skip thresholds so we can access them easily later
        for val in (checks or []):
            if val.upper() in Severities:
                val = val.upper()
                if not self.check_threshold or self.check_threshold.level > Severities[val].level:
                    self.check_threshold = Severities[val]
            else:
                self.checks.append(val)
        # Get regex patterns to split checks and remove it from skip checks:
        updated_skip_checks = set(skip_checks)
        for val in (skip_checks or []):
            splitted_check = val.split(":")
            # In case it's not expected pattern
            if len(splitted_check) != 2:
                continue
            self.skip_checks_regex_patterns[splitted_check[0]].append(splitted_check[1])
            updated_skip_checks -= {val}

        skip_checks = list(updated_skip_checks)
        for val in (skip_checks or []):
            if val.upper() in Severities:
                val = val.upper()
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
        self.filtered_policy_ids = filtered_policy_ids or []
        self.run_image_referencer = run_image_referencer
        self.enable_secret_scan_all_files = enable_secret_scan_all_files
        self.block_list_secret_scan = block_list_secret_scan
        self.suppressed_policies: List[str] = []
        self.deep_analysis = deep_analysis
        self.repo_root_for_plan_enrichment = repo_root_for_plan_enrichment
        self.resource_attr_to_omit: DefaultDict[str, Set[str]] = RunnerFilter._load_resource_attr_to_omit(
            resource_attr_to_omit
        )

    @staticmethod
    def _load_resource_attr_to_omit(resource_attr_to_omit_input: Optional[Dict[str, Set[str]]]) -> DefaultDict[str, Set[str]]:
        resource_attributes_to_omit: DefaultDict[str, Set[str]] = defaultdict(lambda: set())
        # In order to create new object (and not a reference to the given one)
        if resource_attr_to_omit_input:
            resource_attributes_to_omit.update(resource_attr_to_omit_input)
        return resource_attributes_to_omit

    def apply_enforcement_rules(self, enforcement_rule_configs: Dict[str, CodeCategoryConfiguration]) -> None:
        self.enforcement_rule_configs = {}
        for report_type, code_category in CodeCategoryMapping.items():
            config = enforcement_rule_configs.get(code_category)
            if not config:
                raise Exception(f'Could not find an enforcement rule config for category {code_category} (runner: {report_type})')
            self.enforcement_rule_configs[report_type] = config.soft_fail_threshold

    def should_run_check(
            self,
            check: BaseCheck | BaseGraphCheck | None = None,
            check_id: str | None = None,
            bc_check_id: str | None = None,
            severity: Severity | None = None,
            report_type: str | None = None,
            file_origin_paths: List[str] | None = None,
            root_folder: str | None = None
    ) -> bool:
        if check:
            check_id = check.id
            bc_check_id = check.bc_id
            severity = check.severity

        assert check_id is not None  # nosec (for mypy (and then for bandit))

        # apply enforcement rules if specified, but let --check/--skip-check with a severity take priority
        if self.use_enforcement_rules and report_type:
            if not self.check_threshold and not self.skip_check_threshold:
                check_threshold = self.enforcement_rule_configs[report_type]  # type:ignore[index] # mypy thinks it might be null
                skip_check_threshold = None
            else:
                check_threshold = self.check_threshold
                skip_check_threshold = self.skip_check_threshold
        else:
            if self.use_enforcement_rules:
                # this is a warning for us (but there is nothing the user can do about it)
                logging.debug(f'Use enforcement rules is true, but check {check_id} was not passed to the runner filter with a report type')
            check_threshold = self.check_threshold
            skip_check_threshold = self.skip_check_threshold

        run_severity = severity and check_threshold and severity.level >= check_threshold.level
        explicit_run = self.checks and self.check_matches(check_id, bc_check_id, self.checks)
        implicit_run = not self.checks and not check_threshold
        is_external = RunnerFilter.is_external_check(check_id)
        is_policy_filtered = self.is_policy_filtered(check_id)
        # True if this check is present in the allow list, or if there is no allow list
        # this is not necessarily the return value (need to apply other filters)
        should_run_check = (
            run_severity or
            explicit_run or
            implicit_run or
            (is_external and self.all_external)
        )

        if not should_run_check:
            logging.debug(f'Should run check {check_id}: False')
            return False

        # If a policy is not present in the list of filtered policies, it should not be run - implicitly or explicitly.
        # It can, however, be skipped.
        if not is_policy_filtered:
            logging.debug(f'not is_policy_filtered {check_id}: should_run_check = False')
            should_run_check = False

        skip_severity = severity and skip_check_threshold and severity.level <= skip_check_threshold.level
        explicit_skip = self.skip_checks and self.check_matches(check_id, bc_check_id, self.skip_checks)
        regex_match = self._match_regex_pattern(check_id, file_origin_paths, root_folder)
        should_skip_check = (
            skip_severity or
            explicit_skip or
            regex_match or
            (not bc_check_id and not self.include_all_checkov_policies and not is_external and not explicit_run) or
            (bc_check_id in self.suppressed_policies and bc_check_id not in self.bc_cloned_checks)
        )
        logging.debug(f'skip_severity = {skip_severity}, explicit_skip = {explicit_skip}, regex_match = {regex_match}, suppressed_policies: {self.suppressed_policies}')
        logging.debug(
            f'bc_check_id = {bc_check_id}, include_all_checkov_policies = {self.include_all_checkov_policies}, is_external = {is_external}, explicit_run: {explicit_run}')

        if should_skip_check:
            result = False
            logging.debug(f'should_skip_check {check_id}: {should_skip_check}')
        elif should_run_check:
            result = True
            logging.debug(f'should_run_check {check_id}: {result}')
        else:
            result = False
            logging.debug(f'default {check_id}: {result}')

        return result

    def _match_regex_pattern(self, check_id: str, file_origin_paths: List[str] | None, root_folder: str | None) -> bool:
        """
        Check if skip check_id for a certain file_types, according to given path pattern
        """
        if not file_origin_paths:
            return False
        regex_patterns = self.skip_checks_regex_patterns.get(check_id, [])
        # In case skip is generic, for example, CKV_AZURE_*.
        generic_check_id = f"{'_'.join(i for i in check_id.split('_')[:-1])}_*"
        generic_check_regex_patterns = self.skip_checks_regex_patterns.get(generic_check_id, [])
        regex_patterns.extend(generic_check_regex_patterns)
        if not regex_patterns:
            return False

        for pattern in regex_patterns:
            if not pattern:
                continue
            full_regex_pattern = fr"^{root_folder}/{pattern}" if root_folder else pattern
            try:
                if any(re.search(full_regex_pattern, path) for path in file_origin_paths):
                    return True
            except Exception as exc:
                logging.error(
                    "Invalid regex pattern has been supplied",
                    extra={"regex_pattern": pattern, "exc": str(exc)}
                )

        return False

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
    def secret_validation_status_matches(secret_validation_status: str, statuses_list: list[str]) -> bool:
        return secret_validation_status in statuses_list

    @staticmethod
    def notify_external_check(check_id: str) -> None:
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id: str) -> bool:
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS

    def is_policy_filtered(self, check_id: str) -> bool:
        if not self.filtered_policy_ids:
            return True
        return check_id in self.filtered_policy_ids

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            result[key] = value
        return result

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> RunnerFilter:
        framework = obj.get('framework')
        checks = obj.get('checks')
        skip_checks = obj.get('skip_checks')
        include_all_checkov_policies = obj.get('include_all_checkov_policies')
        if include_all_checkov_policies is None:
            include_all_checkov_policies = True
        download_external_modules = obj.get('download_external_modules')
        if download_external_modules is None:
            download_external_modules = False
        external_modules_download_path = obj.get('external_modules_download_path')
        if external_modules_download_path is None:
            external_modules_download_path = DEFAULT_EXTERNAL_MODULES_DIR
        evaluate_variables = obj.get('evaluate_variables')
        if evaluate_variables is None:
            evaluate_variables = True
        runners = obj.get('runners')
        skip_framework = obj.get('skip_framework')
        excluded_paths = obj.get('excluded_paths')
        all_external = obj.get('all_external')
        if all_external is None:
            all_external = False
        var_files = obj.get('var_files')
        skip_cve_package = obj.get('skip_cve_package')
        use_enforcement_rules = obj.get('use_enforcement_rules')
        if use_enforcement_rules is None:
            use_enforcement_rules = False
        filtered_policy_ids = obj.get('filtered_policy_ids')
        show_progress_bar = obj.get('show_progress_bar')
        if show_progress_bar is None:
            show_progress_bar = True
        run_image_referencer = obj.get('run_image_referencer')
        if run_image_referencer is None:
            run_image_referencer = False
        enable_secret_scan_all_files = bool(obj.get('enable_secret_scan_all_files'))
        block_list_secret_scan = obj.get('block_list_secret_scan')
        runner_filter = RunnerFilter(framework, checks, skip_checks, include_all_checkov_policies,
                                     download_external_modules, external_modules_download_path, evaluate_variables,
                                     runners, skip_framework, excluded_paths, all_external, var_files,
                                     skip_cve_package, use_enforcement_rules, filtered_policy_ids, show_progress_bar,
                                     run_image_referencer, enable_secret_scan_all_files, block_list_secret_scan)
        return runner_filter

    def set_suppressed_policies(self, policy_level_suppressions: List[str]) -> None:
        logging.debug(f"Received the following policy-level suppressions, that will be skipped from running: {policy_level_suppressions}")
        self.suppressed_policies = policy_level_suppressions
