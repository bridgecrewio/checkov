from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.typing import _SkippedCheck, _CheckResult
    from checkov.runner_filter import RunnerFilter


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(CheckType.DOCKERFILE)

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # not needed
        pass

    def scan(
        self,
        scanned_file: str,
        entity: dict[str, list[_Instruction]],
        skipped_checks: list[_SkippedCheck],
        runner_filter: RunnerFilter,
        report_type: str | None = None,
    ) -> dict[BaseCheck, _CheckResult]:

        results: "dict[BaseCheck, _CheckResult]" = {}
        if not entity:
            return results
        for instruction, checks in self.checks.items():
            skip_info = {}
            if instruction in entity:

                for check in checks:
                    if check.id in [x['id'] for x in skipped_checks]:
                        skip_info = [x for x in skipped_checks if x['id'] == check.id][0]

                    if runner_filter.should_run_check(check, report_type=CheckType.DOCKERFILE):
                        entity_name = instruction
                        entity_type = instruction
                        entity_configuration = entity[instruction]
                        self.update_result(check, entity_configuration, entity_name, entity_type, results, scanned_file,
                                           skip_info)

        for check in self.wildcard_checks["*"]:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]

            if runner_filter.should_run_check(check, report_type=CheckType.DOCKERFILE):
                entity_name = scanned_file
                entity_type = "*"
                entity_configuration = entity
                self.update_result(check, entity_configuration, entity_name, entity_type, results, scanned_file,
                                   skip_info)
        return results

    def update_result(self, check, entity_configuration, entity_name, entity_type, results, scanned_file, skip_info):
        result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file,
                                skip_info)
        results[check] = {}
        if result['result'] == CheckResult.SKIPPED:
            results[check]['result'] = result['result']
            results[check]['suppress_comment'] = result['suppress_comment']
            results[check]['results_configuration'] = None
        else:
            results[check]['result'] = result['result'][0]
            results[check]['results_configuration'] = result['result'][1]
