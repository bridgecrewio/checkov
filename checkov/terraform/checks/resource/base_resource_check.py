from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, List, Any, Optional

from checkov.common.checks.base_check import BaseCheck
from checkov.common.graph.graph_builder.deterministic import idempotent_dynamic_blocks_enabled
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.var_utils import is_terraform_variable_dependent
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.parser_functions import expand_dynamic_values_completely, handle_dynamic_values


class BaseResourceCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        guideline: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type="resource",
            guideline=guideline,
        )
        self.supported_resources = supported_resources
        resource_registry.register(self)

    @staticmethod
    def _is_variable_dependant(value: Any) -> bool:
        return is_terraform_variable_dependent(value)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        if idempotent_dynamic_blocks_enabled():
            expanded = expand_dynamic_blocks_once(conf)
            self._dynamic_expanded_conf_id = id(expanded)
            try:
                return self.scan_resource_conf(expanded)
            finally:
                self._dynamic_expanded_conf_id = None
        handle_dynamic_values(conf)
        return self.scan_resource_conf(conf)

    def handle_dynamic_values_unless_expanded(self, conf: Dict[str, List[Any]]) -> None:
        """The value-check base classes call this from scan_resource_conf; upstream they call handle_dynamic_values
        a second time on the same conf (a second copy of every unrendered dynamic block)."""
        if id(conf) == getattr(self, "_dynamic_expanded_conf_id", None):
            return
        handle_dynamic_values(conf)

    @abstractmethod
    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        self.evaluated_keys should be set with a JSONPath of the attribute inspected.
        If not relevant it should be set to an empty array so the previous check's value gets overridden in the report.
        """
        raise NotImplementedError()


def expand_dynamic_blocks_once(conf: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    """A private copy of `conf` with every dynamic block expanded exactly once; `conf` itself is not modified."""
    expanded: Dict[str, List[Any]] = pickle_deepcopy(conf)
    expand_dynamic_values_completely(expanded)
    return expanded
