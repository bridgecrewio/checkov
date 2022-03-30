from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class Tiller(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Tiller (Helm v2) is not deployed"
        id = "CKV_K8S_34"
        supported_resources = ["kubernetes_pod"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "metadata" in conf and isinstance(conf["metadata"], list):
            metadata = conf.get("metadata")[0]

            if metadata.get("labels") and isinstance(metadata.get("labels"), list) and isinstance(metadata.get("labels")[0], dict):
                labels = metadata.get("labels")[0]
                self.evaluated_keys = ["metadata/[0]/labels"]
                if labels.get("app") == "helm":
                    self.evaluated_keys = ["metadata/[0]/labels/[0]/app"]
                    return CheckResult.FAILED
                elif labels.get("name") == "tiller":
                    self.evaluated_keys = ["metadata/[0]/labels/[0]/name"]
                    return CheckResult.FAILED

        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]

        containers = spec.get("container")
        for idx, container in enumerate(containers):
            if not isinstance(container, dict):
                return CheckResult.UNKNOWN
            if container.get("image") and isinstance(container.get("image"), list):
                image = container.get("image")[0]
                if "tiller" in image:
                    self.evaluated_keys = [f'spec/[0]/container/[{idx}]/image']
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = Tiller()
