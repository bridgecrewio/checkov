import json
from abc import abstractmethod
from typing import Dict, List, Any

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.registry import resource_registry


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
        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        self.handle_dynamic_values(conf)
        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        self.evaluated_keys should be set with a JSONPath of the attribute inspected.
        If not relevant it should be set to an empty array so the previous check's value gets overridden in the report.
        """
        raise NotImplementedError()

    def handle_dynamic_values(self, conf: Dict[str, List[Any]]) -> None:
        # recursively search for blocks that are dynamic
        for block_name in conf.keys():
            if isinstance(conf[block_name], dict):
                self.handle_dynamic_values(conf[block_name])

            # if the configuration is a block element, search down again.
            if isinstance(conf[block_name], list) and len(conf[block_name]) > 0 and isinstance(conf[block_name][0], dict):
                self.handle_dynamic_values(conf[block_name][0])

        self.process_dynamic_values(conf)

    def process_dynamic_values(self, conf: Dict[str, List[Any]]) -> None:
        for dynamic_element in conf.get("dynamic", {}):
            if isinstance(dynamic_element, str):
                try:
                    dynamic_element = json.loads(dynamic_element)
                except Exception:
                    dynamic_element = {}

            for element_name in dynamic_element.keys():
                conf[element_name] = dynamic_element[element_name].get("content", [])
