import logging
import fnmatch
from typing import Set, Optional, Union, List

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list


class RunnerFilter(object):
    # NOTE: This needs to be static because different filters may be used at load time versus runtime
    #       (see note in BaseCheckRegistery.register). The concept of which checks are external is
    #       logically a "static" concept anyway, so this makes logical sense.
    __EXTERNAL_CHECK_IDS: Set[str] = set()

    def __init__(
        self,
        framework: str = "all",
        checks: Union[str, List[str], None] = None,
        skip_checks: Union[str, List[str], None] = None,
        download_external_modules: bool = False,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        evaluate_variables: bool = True,
        runners: Optional[List[str]] = None,
        skip_framework: Optional[str] = None,
        excluded_paths: Optional[List[str]] = None,
        all_external: bool = False,
        var_files: Optional[List[str]] = None
    ) -> None:

        self.checks = convert_csv_string_arg_to_list(checks)
        self.skip_checks = convert_csv_string_arg_to_list(skip_checks)

        if skip_framework is None:
            self.framework = framework
        else:
            if isinstance(skip_framework, str):
                if framework == "all":
                    if runners is None:
                        runners = []

                    selected_frameworks = list(set(runners) - set(skip_framework.split(",")))
                    self.framework = ",".join(selected_frameworks)
                else:
                    selected_frameworks = list(set(framework.split(",")) - set(skip_framework.split(",")))
                    self.framework = ",".join(selected_frameworks)
        logging.info(f"Resultant set of frameworks (removing skipped frameworks): {self.framework}")

        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.evaluate_variables = evaluate_variables
        self.excluded_paths = excluded_paths
        self.all_external = all_external
        self.var_files = var_files

    def should_run_check(self, check_id: str, bc_check_id: Optional[str] = None) -> bool:
        if RunnerFilter.is_external_check(check_id) and self.all_external:
            pass  # enabled unless skipped
        elif self.checks:
            if self.checks and any((fnmatch.fnmatch(check_id, pattern) or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern))) for pattern in self.checks):
                return True
            else:
                return False
        if self.skip_checks and any((fnmatch.fnmatch(check_id, pattern) or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern))) for pattern in self.skip_checks):
            return False
        return True

    @staticmethod
    def notify_external_check(check_id: str) -> None:
        RunnerFilter.__EXTERNAL_CHECK_IDS.add(check_id)

    @staticmethod
    def is_external_check(check_id: str) -> bool:
        return check_id in RunnerFilter.__EXTERNAL_CHECK_IDS
