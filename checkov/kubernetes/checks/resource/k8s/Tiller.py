from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class Tiller(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Ensure that Tiller (Helm v2) is not deployed"
        id = "CKV_K8S_34"
        # Location: container .image
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["image"]
        return CheckResult.FAILED if Tiller.is_tiller(metadata, conf) else CheckResult.PASSED

    @staticmethod
    def is_tiller(metadata: Dict[str, Any], conf: Dict[str, Any]) -> bool:
        image = conf.get("image")
        if image and isinstance(image, str) and "tiller" in image:
            return True

        if metadata:
            labels = metadata.get("labels")
            if labels:
                if labels.get("app") == "helm":
                    return True
                elif labels.get("name") == "tiller":
                    return True

        return False


check = Tiller()
