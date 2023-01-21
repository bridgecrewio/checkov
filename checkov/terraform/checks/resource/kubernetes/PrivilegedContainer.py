from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class PrivilegedContainers(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.1
        # CIS-1.5 5.2.1
        name = "Do not admit privileged containers"
        id = "CKV_K8S_16"

        supported_resources = ['kubernetes_pod', "kubernetes_pod_v1",
                               'kubernetes_deployment', 'kubernetes_deployment_v1']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        if not spec:
            return CheckResult.UNKNOWN

        evaluated_keys_path = "spec"

        template = spec.get("template")
        if template and isinstance(template, list):
            template = template[0]
            template_spec = template.get("spec")
            if template_spec and isinstance(template_spec, list):
                spec = template_spec[0]
                evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

        if spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if type(container) != dict:
                    return CheckResult.UNKNOWN
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("privileged") == [True]:
                        self.evaluated_keys = [f'{evaluated_keys_path}/[0]/container/[{idx}]/security_context/[0]/privileged']
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = PrivilegedContainers()
