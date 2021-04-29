import json
from abc import abstractmethod
from typing import Dict, List, Callable, Optional

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.multi_signature import multi_signature
from checkov.terraform.checks.resource.registry import resource_registry


class BaseResourceCheck(BaseCheck):
    def __init__(self, name: str, id: str, categories: List[CheckCategories], supported_resources: List[str]) -> None:
        super().__init__(
            name=name, id=id, categories=categories, supported_entities=supported_resources, block_type="resource"
        )
        self.supported_resources = supported_resources
        resource_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List], entity_type: str) -> CheckResult:
        if conf.get("count") == [0]:
            return CheckResult.UNKNOWN

        self.handle_dynamic_values(conf)
        return self.scan_resource_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf: Dict[str, List], entity_type: str) -> CheckResult:
        """
        self.evaluated_keys should be set with a JSONPath of the attribute inspected.
        If not relevant it should be set to an empty array so the previous check's value gets overridden in the report.
        """
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped: Callable) -> Callable:
        def wrapper(self: "BaseResourceCheck", conf: Dict[str, List], entity_type: Optional[str] = None) -> CheckResult:
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper

    def handle_dynamic_values(self, conf: Dict[str, List]) -> None:
        for dynamic_element in conf.get("dynamic", {}):
            if isinstance(dynamic_element, str):
                try:
                    dynamic_element = json.loads(dynamic_element)
                except Exception:
                    dynamic_element = {}
            for element_name in dynamic_element.keys():
                conf[element_name] = dynamic_element[element_name].get("content", [])
