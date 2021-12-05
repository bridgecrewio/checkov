from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ReadinessProbe(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Readiness Probe Should be Configured"
        id = "CKV_K8S_9"
        # Location: container .readinessProbe
        # Don't check Job/CronJob
        supported_entities = [
            entity for entity in BaseK8sContainerCheck.SUPPORTED_ENTITIES if entity not in ("CronJob", "Job")
        ]
        # initContainers do not need Readiness Probes...
        supported_container_types = ["containers"]
        super().__init__(
            name=name, id=id, supported_entities=supported_entities, supported_container_types=supported_container_types
        )

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["readinessProbe"]
        if conf.get("readinessProbe"):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = ReadinessProbe()
