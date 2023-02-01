from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.output.record import Record

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity
    from checkov.common.typing import _CheckResult


class Policy3dRecord(Record):
    def __init__(
        self,
        check_id: str,
        bc_check_id: str | None,
        check_name: str,
        check_result: _CheckResult,
        code_block: list[tuple[int, str]],
        file_path: str,
        file_line_range: list[int],
        resource: str,
        evaluations: dict[str, Any] | None,
        check_class: str,
        file_abs_path: str,
        vulnerabilities: list[dict[str, Any]],
        entity_tags: dict[str, str] | None = None,
        severity: Severity | None = None,
    ) -> None:
        super().__init__(
            check_id=check_id,
            bc_check_id=bc_check_id,
            check_name=check_name,
            check_result=check_result,
            code_block=code_block,
            file_path=file_path,
            file_line_range=file_line_range,
            resource=resource,
            evaluations=evaluations,
            check_class=check_class,
            file_abs_path=file_abs_path,
            entity_tags=entity_tags,
            severity=severity,
        )
        self.vulnerabilities = vulnerabilities
