from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, Any, Optional

from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.checks.resource.registry import registry


def is_rollout_without_template(conf: Dict[str, Any]) -> bool:
    """An Argo Rollout using spec.workloadRef has no pod template of its own. Its pods come from
    the referenced Deployment, which is scanned itself, so pod spec checks don't apply to it."""
    return conf.get("kind") == "Rollout" and not find_in_dict(input_dict=conf, key_path="spec/template")


class BaseK8Check(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_entities: "Iterable[str]",
        guideline: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type="k8",
            guideline=guideline
        )
        self.supported_specs = supported_entities
        registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        self.entity_type = entity_type
        return self.scan_spec_conf(conf)

    @abstractmethod
    def scan_spec_conf(self, conf: Dict[str, Any]) -> CheckResult:
        """Return result of Kubernetes object check."""
        raise NotImplementedError()
