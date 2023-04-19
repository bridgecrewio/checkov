from __future__ import annotations

from typing import Optional, Dict, Any, TYPE_CHECKING


from checkov.common.graph.checks_infra.enums import SolverType
from checkov.policies_3d.syntax.syntax import Predicament

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity
    from checkov.policies_3d.runner import CVECheckAttribute


class Base3dPolicyCheck:
    def __init__(self) -> None:
        self.id = ""
        self.bc_id = ""
        self.name = ""
        self.category = ""
        self.type: Optional[SolverType] = None
        self.guideline: Optional[str] = None
        self.severity: Optional[Severity] = None
        self.bc_category: Optional[str] = None
        self.iac: Dict[str, Any] = {}
        self.cve: Dict[CVECheckAttribute, Any] = {}
        self.predicaments: list[Predicament] = []
