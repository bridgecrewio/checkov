from typing import Dict, Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class DropCapabilitiesPSP(BaseK8Check):
    def __init__(self) -> None:
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.7
        name = "Do not admit containers with the NET_RAW capability"
        # Location: PodSecurityPolicy.spec.requiredDropCapabilities
        id = "CKV_K8S_7"
        supported_kind = ("PodSecurityPolicy",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: Dict[str, Any]) -> CheckResult:
        spec = conf.get("spec")
        if spec and isinstance(spec, dict):
            drop_cap = spec.get("requiredDropCapabilities")
            if drop_cap and isinstance(drop_cap, list):
                if any(cap in drop_cap for cap in ("ALL", "NET_RAW")):
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["spec/requiredDropCapabilities"]


check = DropCapabilitiesPSP()
