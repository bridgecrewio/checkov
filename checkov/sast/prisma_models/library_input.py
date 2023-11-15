from typing import Set, List

from checkov.common.bridgecrew.severities import Severity
from checkov.common.sast.consts import SastLanguages
import sys
if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, NotRequired
else:
    from typing import TypedDict, NotRequired


class LibraryInput(TypedDict):
    languages: Set[SastLanguages]
    source_codes: List[str]
    policies: List[str]
    checks: List[str]
    skip_checks: List[str]
    skip_path: List[str]
    check_threshold: Severity
    skip_check_threshold: Severity
    list_policies: NotRequired[bool]
    report_imports: bool
    remove_default_policies: NotRequired[bool]
    report_reachability: bool
