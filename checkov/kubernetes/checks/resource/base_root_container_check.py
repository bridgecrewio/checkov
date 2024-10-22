from __future__ import annotations

from abc import abstractmethod
from typing import Dict, Any, Optional

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.kubernetes.checks.resource.registry import registry


class BaseK8sRootContainerCheck(BaseK8Check):

    def __init__(
            self,
            name: str,
            id: str,
            guideline: Optional[str] = None,
    ) -> None:
        supported_kind = ('Pod', 'Deployment', 'DaemonSet', 'StatefulSet', 'ReplicaSet', 'ReplicationController',
                          'Job', 'CronJob')
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind,
                         guideline=guideline)
        registry.register(self)

    @abstractmethod
    def scan_spec_conf(self, conf: Dict[str, Any]) -> CheckResult:
        """Return result of Kubernetes rooot container check."""
        raise NotImplementedError()

    def extract_spec(self, conf: Dict[str, Any]) -> Dict[str, Any]:
        spec = {}

        if conf['kind'] == 'Pod':
            if "spec" in conf:
                spec = conf["spec"]
        elif conf['kind'] == 'CronJob':
            inner_spec = find_in_dict(input_dict=conf, key_path="spec/jobTemplate/spec/template/spec")
            spec = inner_spec if inner_spec else spec
        else:
            inner_spec = find_in_dict(input_dict=conf, key_path="spec/template/spec")
            spec = inner_spec if inner_spec else spec
        return spec

    @staticmethod
    def check_runAsNonRoot(spec: dict[str, Any]) -> str:
        if not isinstance(spec, dict):
            return "ABSENT"
        security_context = spec.get("securityContext")
        if security_context and isinstance(security_context, dict) and "runAsNonRoot" in security_context:
            if security_context["runAsNonRoot"]:
                return "PASSED"
            else:
                return "FAILED"
        return "ABSENT"

    @staticmethod
    def check_runAsUser(spec: Dict[str, Any], uid: int) -> str:
        if isinstance(spec, dict) and spec.get("securityContext") and isinstance(spec.get("securityContext"), dict) and "runAsUser" in spec["securityContext"]:
            if isinstance(spec["securityContext"]["runAsUser"], int) and spec["securityContext"]["runAsUser"] >= uid:
                return "PASSED"
            else:
                return "FAILED"
        return "ABSENT"
