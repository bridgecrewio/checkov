from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ReadonlyRootFilesystem(BaseResourceCheck):

    def __init__(self):
        name = "Use read-only filesystem for containers where possible"
        id = "CKV_K8S_22"

        supported_resources = ['kubernetes_pod', "kubernetes_pod_v1",
                               'kubernetes_deployment', 'kubernetes_deployment_v1']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        evaluated_keys_path = "spec"
        if not spec:
            return CheckResult.UNKNOWN
        if spec.get("template") and isinstance(spec.get("template"), list):
            template = spec.get("template")[0]
            if template.get("spec") and isinstance(template.get("spec"), list):
                spec = template.get("spec")[0]
                evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

        if isinstance(spec, dict) and spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("read_only_root_filesystem") != [True]:
                        self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]/security_context/[0]/read_only_root_filesystem']
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = ReadonlyRootFilesystem()
