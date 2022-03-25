import itertools
from typing import Optional, Tuple, List, Dict, Any, TYPE_CHECKING

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.checks_infra.solvers.base_solver import BaseSolver

if TYPE_CHECKING:
    from checkov.common.bridgecrew.severities import Severity


class BaseGraphCheck:
    def __init__(self) -> None:
        self.id = ""
        self.bc_id = None
        self.name = ""
        self.category = ""
        self.resource_types: List[str] = []
        self.connected_resources_types: List[str] = []
        self.operator = ""
        self.attribute: Optional[str] = None
        self.attribute_value: Optional[str] = None
        self.sub_checks: List["BaseGraphCheck"] = []
        self.type: Optional[SolverType] = None
        self.solver: Optional[BaseSolver] = None
        self.guideline: Optional[str] = None
        self.benchmarks: Dict[str, List[str]] = {}
        self.severity: Optional[Severity] = None
        self.bc_category: Optional[str] = None

    def set_solver(self, solver: BaseSolver) -> None:
        self.solver = solver

    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        return self.solver.run(graph_connector=graph_connector)

    def get_output_id(self, use_bc_ids: bool) -> str:
        return self.bc_id if self.bc_id and use_bc_ids else self.id

    def get_evaluated_keys(self) -> List[str]:
        if self.sub_checks:
            return list(set(itertools.chain.from_iterable(check.get_evaluated_keys() for check in self.sub_checks)))
        return ["/".join(self.attribute.split('.'))] if self.attribute else []
