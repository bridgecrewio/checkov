from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class Secrets(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.5 5.4.1
        name = "Prefer using secrets as files over secrets as environment variables"
        id = "CKV_K8S_35"
        # Location: container .env
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["env", "envFrom"]
        if conf.get("env"):
            for idx, e in enumerate(conf["env"]):
                if not isinstance(e, dict):
                    return CheckResult.UNKNOWN
                value_from = e.get("valueFrom")
                if value_from and "secretKeyRef" in value_from:
                    self.evaluated_container_keys = [f"env/[{idx}]/valueFrom/secretKeyRef"]
                    return CheckResult.FAILED
        if conf.get("envFrom"):
            for idx, ef in enumerate(conf["envFrom"]):
                if "secretRef" in ef:
                    self.evaluated_container_keys = [f"envFrom/[{idx}]/secretRef"]
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = Secrets()
