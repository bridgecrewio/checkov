from typing import Optional

from typing_extensions import TypedDict


class _SkippedCheck(TypedDict, total=False):
    bc_id: Optional[str]
    id: str
    suppress_comment: str
