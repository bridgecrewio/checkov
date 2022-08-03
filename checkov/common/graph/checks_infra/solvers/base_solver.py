from abc import abstractmethod
from typing import Tuple, List, Dict, Any

from networkx import DiGraph

from checkov.common.graph.checks_infra.enums import SolverType


class BaseSolver:
    operator = ""  # noqa: CCE003  # a static attribute

    def __init__(self, solver_type: SolverType) -> None:
        self.solver_type = solver_type

    @abstractmethod
    def get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError()

    @staticmethod
    def resource_type_pred(v: Dict[str, Any], resource_types: List[str]) -> bool:
        return not resource_types or ("resource_type" in v and v["resource_type"] in resource_types)
