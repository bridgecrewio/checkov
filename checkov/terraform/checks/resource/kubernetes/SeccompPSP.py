from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SeccompPSP(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.7.2
        name = "Ensure default seccomp profile set to docker/default or runtime/default"
        id = "CKV_K8S_32"
        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "metadata" in conf:
            self.evaluated_keys = ["metadata"]
            if "annotations" in conf["metadata"][0]:
                self.evaluated_keys = ["metadata/[0]/annotations"]
                metadata = conf["metadata"][0]
                if metadata.get("annotations"):
                    annotations = metadata["annotations"][0]
                    if annotations is not None:
                        for annotation in annotations:
                            annotation = ''.join(annotation.split())
                            if annotation == "seccomp.security.alpha.kubernetes.io/defaultProfileName":
                                my_value = str(annotations.get(annotation))
                                if "docker/default" in my_value or "runtime/default" in my_value:
                                    return CheckResult.PASSED
        return CheckResult.FAILED


check = SeccompPSP()
