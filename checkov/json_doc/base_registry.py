from __future__ import annotations

from typing import Any, Dict, List, Callable

from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _SkippedCheck
from checkov.json_doc.enums import BlockType
from checkov.runner_filter import RunnerFilter


class Registry(BaseCheckRegistry):
    def __init__(self, report_type: str) -> None:  # TODO set default to JSON
        super().__init__(report_type=report_type)
        self._scanner: Dict[str, Callable[[str, Any, Any, Any, str, str, Dict[str, Any]], None]] = {
            BlockType.ARRAY: self._scan_json_array,
            BlockType.OBJECT: self._scan_json_object,
        }

    def _scan_json_array(
        self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: List[Dict[str, Any]],
            entity_name: str, entity_type: str, results: Dict[str, Any]
    ) -> None:
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

    def _scan_json_object(
        self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: Dict[str, Any],
            entity_name: str, entity_type: str, results: Dict[str, Any]
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

    def _scan_json_document(
        self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: Dict[str, Any], entity_name: str,
            entity_type: str, results: Dict[str, Any]
    ) -> None:
        self.update_result(
            check, entity, entity_name, entity_type, results, scanned_file, skip_info
        )

    def _scan_json(
        self,
        scanned_file: str,
        checks: List[BaseCheck],
        skipped_checks: List[_SkippedCheck],
        runner_filter: RunnerFilter,
        entity: Dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: Dict[str, Any],
    ) -> None:
        for check in checks:
            skip_info = ([x for x in skipped_checks if x["id"] == check.id] or [{}])[0]

            if runner_filter.should_run_check(check=check, report_type=self.report_type):
                scanner: Callable[[str, Any, Any, Any, str, str, Dict[str, Any]], None] = self._scanner.get(check.block_type, self._scan_json_document)
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
        entity: Dict[str, Any],
        skipped_checks: List[_SkippedCheck],
        runner_filter: RunnerFilter
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        if not entity:
            return results

        for instruction, checks in self.checks.items():
            self._scan_json(
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
            self._scan_json(
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
        entity_configuration: Dict[str, Any],
        entity_name: str,
        entity_type: str,
        results: Dict[str, Any],
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

        result = check_result["result"]
        result_key = f'{entity_type}.{entity_name}.{check.id}'

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
        evaluated_keys = check_result.get('evaluated_keys', [])
        results[result_key] = {
            "check": check,
            "result": result,
            "results_configuration": self.get_result_configuration(evaluated_keys, entity_configuration),
        }
        return result

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # not used, but is an abstractmethod
        return "", "", {}

    @staticmethod
    def get_result_configuration(evaluated_keys: list[str], entity_conf: dict[str, Any] | list[Any]) \
            -> dict[str, Any] | list[str | dict[str, Any]]:
        if len(evaluated_keys) == 1 and isinstance(entity_conf, dict):
            # the result configuration should be the smallest code block found by the evaluated_key path, that is of \
            # type dict or list - the only types that currently have start_mark and end_mark lines configured
            for path in evaluated_keys[0].split('/'):
                reduced_conf = entity_conf.get(path)  # type:ignore[union-attr]
                if not reduced_conf or isinstance(reduced_conf, str):
                    return entity_conf
                entity_conf = reduced_conf

        return entity_conf
