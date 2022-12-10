from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DropCapabilities(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.7
        # NET_RAW allows a process to spy on packets on its network
        name = "Minimize the admission of containers with the NET_RAW capability"
        id = "CKV_K8S_28"

        supported_resources = ('kubernetes_pod', 'kubernetes_pod_v1',
                               'kubernetes_deployment', 'kubernetes_deployment_v1', )
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]
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
                dropped = False
                if container.get("security_context") and isinstance(container.get("security_context"), list):
                    context = container.get("security_context")[0]
                    if context.get("capabilities") and isinstance(context.get("capabilities"), list):
                        capabilities = context.get("capabilities")[0]
                        if isinstance(capabilities, dict) and capabilities.get("drop") and isinstance(capabilities.get("drop"), list):
                            drops = capabilities.get("drop")[0]
                            for drop in drops:
                                if drop in ["ALL", "NET_RAW"]:
                                    dropped = True
                            if not dropped:
                                return CheckResult.FAILED
                        else:
                            self.evaluated_keys = [f"{evaluated_keys_path}/[0]/container/{idx}/security_context/[0]/capabilities"]
                            return CheckResult.FAILED
                    else:
                        self.evaluated_keys = [f"{evaluated_keys_path}/[0]/container/{idx}/security_context"]
                        return CheckResult.FAILED
                else:
                    self.evaluated_keys = [f"{evaluated_keys_path}/[0]/container/{idx}"]
                    return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = DropCapabilities()
