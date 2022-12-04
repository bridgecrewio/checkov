from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

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
        return "", "", {}

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

        skipped_check_ids = {skipped_check["id"]: skipped_check for skipped_check in skipped_checks}

        for instruction, checks in self.checks.items():
            if instruction in entity:
                for check in checks:
                    skip_info: "_SkippedCheck" = {}
                    if skipped_check_ids:
                        if check.id in skipped_check_ids:
                            skip_info = skipped_check_ids[check.id]

                    if runner_filter.should_run_check(check, report_type=CheckType.DOCKERFILE):
                        self.update_result(
                            check=check,
                            entity_configuration=entity[instruction],
                            entity_name=instruction,
                            entity_type=instruction,
                            results=results,
                            scanned_file=scanned_file,
                            skip_info=skip_info,
                        )

        for check in self.wildcard_checks["*"]:
            skip_info = {}
            if skipped_check_ids:
                if check.id in skipped_check_ids:
                    skip_info = skipped_check_ids[check.id]

            if runner_filter.should_run_check(check, report_type=CheckType.DOCKERFILE):
                self.update_result(
                    check=check,
                    entity_configuration=entity,
                    entity_name=scanned_file,
                    entity_type="*",
                    results=results,
                    scanned_file=scanned_file,
                    skip_info=skip_info,
                )
        return results

    def update_result(
        self,
        check: BaseCheck,
        entity_configuration: list[_Instruction] | dict[str, list[_Instruction]],
        entity_name: str,
        entity_type: str,
        results: dict[BaseCheck, _CheckResult],
        scanned_file: str,
        skip_info: _SkippedCheck
    ) -> None:
        result = self.run_check(
            check=check,
            entity_configuration=entity_configuration,  # type:ignore[arg-type]  # special Dockerfile runner behaviour
            entity_name=entity_name,
            entity_type=entity_type,
            scanned_file=scanned_file,
            skip_info=skip_info,
        )
        results[check] = {}
        if result['result'] == CheckResult.SKIPPED:
            results[check]['result'] = result['result']
            results[check]['suppress_comment'] = result['suppress_comment']
            results[check]['results_configuration'] = None
        else:
            results[check]['result'] = cast("CheckResult", result['result'][0])
            results[check]['results_configuration'] = cast("dict[str, Any]", result['result'][1])
