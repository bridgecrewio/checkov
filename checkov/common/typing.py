from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckResult
    from checkov.common.checks.base_check import BaseCheck


class _CheckResult(TypedDict, total=False):
    result: "CheckResult"
    suppress_comment: str
    evaluated_keys: list[str]
    results_configuration: Optional[dict]
    check: BaseCheck


class _SkippedCheck(TypedDict, total=False):
    bc_id: str | None
    id: str
    suppress_comment: str
