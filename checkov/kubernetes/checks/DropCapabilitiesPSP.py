from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class DropCapabilitiesPSP(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.7
        name = "Do not admit containers with the NET_RAW capability"
        # Location: PodSecurityPolicy.spec.requiredDropCapabilities
        id = "CKV_K8S_7"
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if "metadata" in conf:
            if "name" in conf["metadata"]:
                return 'PodSecurityPolicy.{}'.format(conf["metadata"]["name"])
        return 'PodSecurityPolicy.spec.requiredDropCapabilities'

    def scan_spec_conf(self, conf):
        if "spec" in conf:
            if "requiredDropCapabilities" in conf["spec"]:
                if "ALL" in conf["spec"]["requiredDropCapabilities"] or "NET_RAW" in conf["spec"][
                    "requiredDropCapabilities"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = DropCapabilitiesPSP()
