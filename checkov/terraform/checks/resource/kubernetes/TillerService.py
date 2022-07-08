from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class TillerService(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that the Tiller Service (Helm v2) is deleted"
        id = "CKV_K8S_44"
        supported_resources = ["kubernetes_service"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "metadata" in conf and isinstance(conf["metadata"], list):
            metadata = conf.get("metadata")[0]

            if metadata.get("labels") and isinstance(metadata.get("labels"), list) \
                    and isinstance(metadata.get("labels")[0], dict):
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

        if spec.get('selector') and isinstance(spec.get('selector'), list):
            selector = spec.get('selector')[0]
            if selector and isinstance(selector, dict):
                for v in selector.values():
                    test = str(v).lower()
                    if 'tiller' in test:
                        self.evaluated_keys = ["spec/[0]/selector/app"]
                        return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = TillerService()
