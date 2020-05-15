from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class SeccompPSP(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.2
        name = "Ensure default seccomp profile set to docker/default or runtime/default"
        id = "CKV_K8S_32"
        # Location: PodSecurityPolicy.annotations.seccomp.security.alpha.kubernetes.io/defaultProfileName
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        if "metadata" in conf:
            if "name" in conf["metadata"]:
                return 'PodSecurityPolicy.{}'.format(conf["metadata"]["name"])
        return 'PodSecurityPolicy.annotations.seccomp.security.alpha.kubernetes.io/defaultProfileName'

    def scan_spec_conf(self, conf):
        if "metadata" in conf:
            if "annotations" in conf["metadata"]:
                if "seccomp.security.alpha.kubernetes.io/defaultProfileName" in conf["metadata"]["annotations"]:
                    if ("docker/default" in conf["metadata"]["annotations"]["seccomp.security.alpha.kubernetes.io/defaultProfileName"] or
                        "runtime/default" in conf["metadata"]["annotations"]["seccomp.security.alpha.kubernetes.io/defaultProfileName"]):
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = SeccompPSP()
