from __future__ import annotations

from typing import Optional, Dict, Any, TYPE_CHECKING


from checkov.common.graph.checks_infra.enums import SolverType

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity


class Base3dPolicyCheck:
    def __init__(self) -> None:
        self.id = ""
        self.bc_id = None
        self.name = ""
        self.category = ""
        self.type: Optional[SolverType] = None
        self.guideline: Optional[str] = None
        self.severity: Optional[Severity] = None
        self.bc_category: Optional[str] = None
        self.iac: Dict[str, Any] = {}
        self.cve: Dict[str, Any] = {}
