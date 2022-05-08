from __future__ import annotations

from typing import Any, Dict, List

from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _SkippedCheck, _ScannerCallableAlias
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.enums import BlockType
import jmespath


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__()
        self._scanner: dict[str, _ScannerCallableAlias] = {
            BlockType.ARRAY: self._scan_yaml_array,
            BlockType.OBJECT: self._scan_yaml_object,
        }

    def _scan_yaml_array(
            self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: Dict[str, Any],
            entity_name: str,
            entity_type: str, results: Dict[str, Any]
    ) -> None:
        if isinstance(entity, dict):
            analyzed_entities = jmespath.search(entity_type, entity)
            if isinstance(analyzed_entities, dict):
                for item, item_conf in analyzed_entities.items():
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
            if isinstance(analyzed_entities, list):
                for item in analyzed_entities:
                    if '__startline__' != item and '__endline__' != item:
                        self.update_result(
                            check,
                            item,
                            entity_type,
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

    def _scan_yaml_object(
            self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: Dict[str, Any],
            entity_name: str,
            entity_type: str, results: Dict[str, Any]
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

    def _scan_yaml_document(
            self, scanned_file: str, check: BaseCheck, skip_info: _SkippedCheck, entity: Dict[str, Any],
            entity_name: str,
            entity_type: str, results: Dict[str, Any]
    ) -> None:
        self.update_result(
            check, entity, entity_name, entity_type, results, scanned_file, skip_info
        )

    def _scan_yaml(
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

            if runner_filter.should_run_check(check=check):
                scanner = self._scanner.get(check.block_type, self._scan_yaml_document)
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
            self._scan_yaml(
                scanned_file=scanned_file,
                checks=checks,
                skipped_checks=skipped_checks,
                runner_filter=runner_filter,
                entity=entity,
                entity_name=instruction,
                entity_type=instruction,
                results=results,
            )

        if self.wildcard_checks:
            for wildcard_pattern in self.wildcard_checks:
                self._scan_yaml(
                    scanned_file=scanned_file,
                    checks=self.wildcard_checks[wildcard_pattern],
                    skipped_checks=skipped_checks,
                    runner_filter=runner_filter,
                    entity=entity,
                    entity_name=scanned_file,
                    entity_type=wildcard_pattern,
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
        result_key = self.get_result_key(check,
                                         entity_configuration,
                                         entity_name,
                                         entity_type,
                                         scanned_file,
                                         skip_info)

        result = check_result["result"]

        if result == CheckResult.SKIPPED:
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

    def get_result_key(self, check: BaseCheck,
                       entity_configuration: Dict[str, Any],
                       entity_name: str,
                       entity_type: str,
                       scanned_file: str,
                       skip_info: _SkippedCheck) -> str:
        if "__startline__" and "__endline__" in entity_configuration:
            return f'{entity_type}.{entity_name}.{check.id}[{entity_configuration["__startline__"]}:{entity_configuration["__endline__"]}]'
        return f'{entity_type}.{entity_name}.{check.id}'

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # not used, but is an abstractmethod
        pass
