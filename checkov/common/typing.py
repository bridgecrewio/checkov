from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckResult


class _CheckResult(TypedDict, total=False):
    result: "CheckResult"
    suppress_comment: str
    evaluated_keys: list[str]


class _SkippedCheck(TypedDict, total=False):
    bc_id: str | None
    id: str
    suppress_comment: str
