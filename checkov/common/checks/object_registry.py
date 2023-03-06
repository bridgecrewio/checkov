from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult
from checkov.common.checks.enums import BlockType
from checkov.common.typing import _SkippedCheck, _ScannerCallableAlias

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.runner_filter import RunnerFilter


class Registry(BaseCheckRegistry):
    def __init__(self, report_type: str) -> None:
        super().__init__(report_type=report_type)
        self._scanner: dict[str, _ScannerCallableAlias] = {
            BlockType.ARRAY: self._scan_array,
            BlockType.OBJECT: self._scan_object,
        }

    def _scan_array(
        self,
        scanned_file: str,
        check: BaseCheck,
        skip_info: _SkippedCheck,
        entity: dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: dict[str, Any],
    ) -> None:
        if isinstance(entity, dict):
            analayzed_dict = entity.get(entity_type, {})
            for item, item_conf in analayzed_dict.items():
                if '__startline__' != item and '__endline__' != item:
                    self.update_result(
                        check,
                        item_conf,
                        item,
                        entity_type,
                        results,
                        scanned_file,
                        skip_info,
                    )
        if isinstance(entity, list):
            for item in entity:
                if entity_name in item:
                    result = self.update_result(
                        check,
                        item[entity_name],
                        entity_name,
                        entity_type,
                        results,
                        scanned_file,
                        skip_info,
                    )
                    if result == CheckResult.FAILED:
                        break

    def _scan_object(
        self,
        scanned_file: str,
        check: BaseCheck,
        skip_info: _SkippedCheck,
        entity: dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: dict[str, Any],
    ) -> None:
        if entity_name in entity:
            self.update_result(
                check,
                entity[entity_name],
                entity_name,
                entity_type,
                results,
                scanned_file,
                skip_info,
            )

    def _scan_document(
        self,
        scanned_file: str,
        check: BaseCheck,
        skip_info: _SkippedCheck,
        entity: dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: dict[str, Any],
    ) -> None:
        self.update_result(
            check, entity, entity_name, entity_type, results, scanned_file, skip_info
        )

    def _scan(
        self,
        scanned_file: str,
        checks: list[BaseCheck],
        skipped_checks: list[_SkippedCheck],
        runner_filter: RunnerFilter,
        entity: dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: dict[str, Any],
    ) -> None:
        for check in checks:
            skip_info = ([x for x in skipped_checks if x["id"] == check.id] or [{}])[0]

            if runner_filter.should_run_check(check=check, report_type=self.report_type):
                scanner = self._scanner.get(check.block_type, self._scan_document)
                if check.path:
                    target = entity
                    for p in check.path.split("."):
                        if p.endswith("]"):
                            ip = p.split("[")
                            i = int(ip[1][:-1])
                            target = target[ip[0]][i]
                        else:
                            target = target[p]
                else:
                    target = entity

                scanner(
                    scanned_file,
                    check,
                    skip_info,
                    target,
                    entity_name,
                    entity_type,
                    results,
                )

    def scan(  # type:ignore[override]  # return type is different than the base class
        self,
        scanned_file: str,
        entity: dict[str, Any],
        skipped_checks: list[_SkippedCheck],
        runner_filter: RunnerFilter,
    ) -> dict[str, Any]:
        results: dict[str, Any] = {}

        if not entity:
            return results

        for instruction, checks in self.checks.items():
            self._scan(
                scanned_file=scanned_file,
                checks=checks,
                skipped_checks=skipped_checks,
                runner_filter=runner_filter,
                entity=entity,
                entity_name=instruction,
                entity_type=instruction,
                results=results,
            )

        if self.wildcard_checks["*"]:
            self._scan(
                scanned_file=scanned_file,
                checks=self.wildcard_checks["*"],
                skipped_checks=skipped_checks,
                runner_filter=runner_filter,
                entity=entity,
                entity_name=scanned_file,
                entity_type="*",
                results=results,
            )

        return results

    def update_result(
        self,
        check: BaseCheck,
        entity_configuration: dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: dict[str, Any],
        scanned_file: str,
        skip_info: _SkippedCheck,
    ) -> CheckResult:
        check_result = self.run_check(
            check,
            entity_configuration,
            entity_name,
            entity_type,
            scanned_file,
            skip_info,
        )
        result_key = self.get_key(entity_type, entity_name, check.id, scanned_file)

        result = check_result["result"]

        if isinstance(result, CheckResult) and result == CheckResult.SKIPPED:
            results[result_key] = {
                "check": check,
                "result": result,
                "suppress_comment": check_result["suppress_comment"],
                "results_configuration": None,
            }
            return result

        if isinstance(result, tuple):
            results[result_key] = {
                "check": check,
                "result": result[0],
                "results_configuration": result[1],
            }
            return result[0]
        results[result_key] = {
            "check": check,
            "result": result,
            "results_configuration": entity_configuration,
        }
        return result

    def get_key(self, entity_type: str, entity_name: str, check_id: str, file_path: str) -> str:
        return f'{entity_type}.{entity_name}.{check_id}'

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # not used, but is an abstractmethod
        return "", "", {}
