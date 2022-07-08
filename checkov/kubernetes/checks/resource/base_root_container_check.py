from abc import abstractmethod
from typing import Dict, Any, Optional

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.multi_signature import multi_signature
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

    @multi_signature()
    @abstractmethod
    def scan_spec_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        """Return result of Kubernetes rooot container check."""
        raise NotImplementedError()

    def extract_spec(self, conf: Dict[str, Any]) -> Dict:
        spec = {}

        if conf['kind'] == 'Pod':
            if "spec" in conf:
                spec = conf["spec"]
        elif conf['kind'] == 'CronJob':
            if "spec" in conf and "jobTemplate" in conf["spec"] and "spec" in conf["spec"]["jobTemplate"] and "template" in conf["spec"]["jobTemplate"]["spec"] and "spec" in conf["spec"]["jobTemplate"]["spec"]["template"]:
                spec = conf["spec"]["jobTemplate"]["spec"]["template"]["spec"]
        else:
            inner_spec = self.get_inner_entry(conf, "spec")
            spec = inner_spec if inner_spec else spec
        return spec

    @staticmethod
    def check_runAsNonRoot(spec):
        security_context = spec.get("securityContext")
        if security_context and isinstance(security_context, dict) and "runAsNonRoot" in security_context:
            if security_context["runAsNonRoot"]:
                return "PASSED"
            else:
                return "FAILED"
        return "ABSENT"

    @staticmethod
    def check_runAsUser(spec: Dict[str, Any], uid: int) -> str:
        if spec.get("securityContext") and isinstance(spec.get("securityContext"), dict) and "runAsUser" in spec["securityContext"]:
            if isinstance(spec["securityContext"]["runAsUser"], int) and spec["securityContext"]["runAsUser"] >= uid:
                return "PASSED"
            else:
                return "FAILED"
        return "ABSENT"
