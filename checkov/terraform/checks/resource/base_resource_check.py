from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, List, Any, Optional

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.parser_functions import handle_dynamic_values
from checkov.terraform.parser_utils import find_var_blocks


PROVIDER_PREFIXES = (
    "aws_",
    "azurerm_",
    "azuread_",
    "digitalocean_",
    "google_",
    "github_",
    "linode_",
    "oci_",
    "openstack_",
)


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
        if not isinstance(value, str):
            return False

        if value.startswith(("var.", "local.", "module.")):
            return True

        if value.startswith(PROVIDER_PREFIXES):
            return True

        if "${" not in value:
            return False

        if find_var_blocks(value):
            return True
        return False

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        handle_dynamic_values(conf)
        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        self.evaluated_keys should be set with a JSONPath of the attribute inspected.
        If not relevant it should be set to an empty array so the previous check's value gets overridden in the report.
        """
        raise NotImplementedError()
