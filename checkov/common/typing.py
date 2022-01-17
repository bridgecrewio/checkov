from typing import Optional, TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckResult


class _CheckResult(TypedDict, total=False):
    result: "CheckResult"
    suppress_comment: str


class _SkippedCheck(TypedDict, total=False):
    bc_id: Optional[str]
    id: str
    suppress_comment: str
