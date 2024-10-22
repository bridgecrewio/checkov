from typing import Optional, List
from checkov.common.bridgecrew.severities import Severity
from checkov.common.models.enums import CheckCategories


class BaseSastCheck:
    def __init__(self, name: str, id: str, severity: Optional[Severity] = None) -> None:
        self.name: str = name
        self.id: str = id
        self.categories: List[CheckCategories] = [CheckCategories.SAST]
        # TODO
        self.guideline: str = ''
        self.severity: Optional[Severity] = severity
        self.bc_id: str = ''
