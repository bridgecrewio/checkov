from __future__ import annotations

from abc import abstractmethod
from typing import Tuple, List, Dict, Any, TYPE_CHECKING

from checkov.common.graph.checks_infra.enums import SolverType
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.env_vars_config import env_vars_config

if TYPE_CHECKING:
    from networkx import DiGraph

# Based on the resource names in iac frameworks
AWS_KEYS = ['aws_', 'AWS::', 'aws-']
GCP_KEYS = ['gcloud', 'google_']
AZURE_KEYS = ['azurerm_', 'Microsoft.']


class BaseSolver:
    operator = ""  # noqa: CCE003  # a static attribute

    def __init__(self, solver_type: SolverType) -> None:
        self.solver_type = solver_type
        self.providers: List[str] = []

    @abstractmethod
    def get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def run(self, graph_connector: DiGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        raise NotImplementedError()

    def resource_type_pred(self, v: Dict[str, Any], resource_types: List[str]) -> bool:
        resource_type = CustomAttributes.RESOURCE_TYPE
        if env_vars_config.CKV_SUPPORT_ALL_RESOURCE_TYPE:
            is_all_resources = isinstance(resource_types, list) and resource_types[0].lower() == "all"
            resource_type_match_provider = self.resource_match_provider(v.get(resource_type, ''))
            support_all_resources = bool(resource_type in v and is_all_resources and v.get(resource_type) != 'module' and resource_type_match_provider)

            return not resource_types or support_all_resources

        return not resource_types or (resource_type in v and v[resource_type] in resource_types)

    def resource_match_provider(self, resource_type: str) -> bool:
        if not self.providers:
            return True
        for provider in self.providers:
            if provider.lower() == 'aws':
                if any(resource_type.startswith(key) for key in AWS_KEYS):
                    return True
            elif provider.lower() == 'gcp':
                if any(resource_type.startswith(key) for key in GCP_KEYS):
                    return True
            elif provider.lower() == 'azure':
                if any(resource_type.startswith(key) for key in AZURE_KEYS):
                    return True
            else:  # if we don't have a provider or the provider was not one of the basic providers
                return True
        return False
