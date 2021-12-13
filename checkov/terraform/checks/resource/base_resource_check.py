from abc import abstractmethod
from typing import Dict, List, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.parser_functions import handle_dynamic_values


class BaseResourceCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: List[CheckCategories], supported_resources: List[str],
                 guideline=None) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_entities=supported_resources,
            block_type="resource", guideline=guideline
        )
        self.supported_resources = supported_resources
        resource_registry.register(self)

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
