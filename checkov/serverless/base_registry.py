from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check_registry import BaseCheckRegistry

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.typing import _SkippedCheck, _CheckResult
    from checkov.runner_filter import RunnerFilter


@dataclass
class EntityDetails:
    provider_type: str | None
    data: dict[str, Any]


class ServerlessRegistry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(CheckType.SERVERLESS)

    def extract_entity_details(self, entity: EntityDetails) -> tuple[str, dict[str, Any]]:  # type:ignore[override]
        return f"serverless_{entity.provider_type}", entity.data

    def scan(  # type:ignore[override]
        self, scanned_file: str, entity: EntityDetails, skipped_checks: list[_SkippedCheck], runner_filter: RunnerFilter
    ) -> dict[BaseCheck, _CheckResult]:
        entity_type, entity_configuration = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info: _SkippedCheck = {}
            if skipped_checks:
                if check.id in [x["id"] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x["id"] == check.id][0]

            if runner_filter.should_run_check(check, report_type=CheckType.SERVERLESS):
                self.logger.debug(f"Running check: {check.name} on file {scanned_file}")
                result = check.run(
                    scanned_file=scanned_file,
                    entity_configuration=entity_configuration,
                    entity_name=entity_type,
                    entity_type=entity_type,
                    skip_info=skip_info,
                )
                results[check] = result
        return results
