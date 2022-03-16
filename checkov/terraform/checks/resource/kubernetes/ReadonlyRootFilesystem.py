from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ReadonlyRootFilesystem(BaseResourceCheck):

    def __init__(self):
        name = "Use read-only filesystem for containers where possible"
        id = "CKV_K8S_22"

        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf['spec'][0]
        if spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("read_only_root_filesystem") != [True]:
                        self.evaluated_keys = [f'spec/[0]/container/[{idx}]/security_context/[0]/read_only_root_filesystem']
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = ReadonlyRootFilesystem()
