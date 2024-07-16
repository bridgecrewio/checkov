from __future__ import annotations

import os
from abc import abstractmethod
from typing import Tuple, List, Dict, Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.util.env_vars_config import env_vars_config
from checkov.common.util.type_forcers import convert_str_to_bool

if TYPE_CHECKING:
    from networkx import DiGraph


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
    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError()

    @staticmethod
    def resource_type_pred(v: Dict[str, Any], resource_types: List[str]) -> bool:
        if env_vars_config.CKV_SUPPORT_ALL_RESOURCE_TYPE:
            is_all_resources = isinstance(resource_types, list) and resource_types[0].lower() == "all"
            support_all_resources = bool("resource_type" in v and is_all_resources and v[
                "resource_type"] != 'module')
        else:
            support_all_resources = False
        return not resource_types or ("resource_type" in v and v["resource_type"] in resource_types) or support_all_resources
