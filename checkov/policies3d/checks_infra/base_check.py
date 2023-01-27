from __future__ import annotations

import itertools
from typing import Optional, Tuple, List, Dict, Any, TYPE_CHECKING


from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity
    from networkx import DiGraph


class Base3dPolicyCheck:
    def __init__(self) -> None:
        self.id = ""
        self.bc_id = None
        self.name = ""
        self.category = ""
        self.type: Optional[SolverType] = None
        self.solver: Optional[BaseSolver] = None
        self.guideline: Optional[str] = None
        self.benchmarks: Dict[str, List[str]] = {}
        self.severity: Optional[Severity] = None
        self.bc_category: Optional[str] = None
        self.frameworks: List[str] = []
        self.check_path: str = ""
        self.iac = []
        self.cve = []

    def set_solver(self, solver: BaseSolver) -> None:
        self.solver = solver

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self.solver:
            raise AttributeError("solver attribute was not set")

        return self.solver.run(graph_connector=graph_connector)
