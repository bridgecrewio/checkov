
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class HostPort(BaseResourceCheck):

    def __init__(self):
        """
               https://kubernetes.io/docs/concepts/configuration/overview/

               Don’t specify a hostPort for a Pod unless it is absolutely necessary.
               When you bind a Pod to a hostPort, it limits the number of places the
               Pod can be scheduled, because each <hostIP, hostPort, protocol> combination
               must be unique.
               """
        name = "Do not specify hostPort unless absolutely necessary"
        id = "CKV_K8S_26"
        supported_resources = ["kubernetes_pod", "kubernetes_pod_v1",
                               "kubernetes_deployment", "kubernetes_deployment_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED

        spec = conf.get('spec')[0]
        evaluated_keys_path = "spec"

        if spec:

            template = spec.get("template")
            if template and isinstance(template, list):
                template = template[0]
                template_spec = template.get("spec")
                if template_spec and isinstance(template_spec, list):
                    spec = template_spec[0]
                    evaluated_keys_path = f'{evaluated_keys_path}/[0]/template/[0]/spec'

            containers = spec.get("container")
            if containers is None:
                return CheckResult.UNKNOWN
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("port"):
                    for idy, port in enumerate(container["port"]):
                        if "host_port" in port:
                            self.evaluated_keys = [f"{evaluated_keys_path}/[0]/container/[{idx}]/port/[{idy}]/host_port"]
                            return CheckResult.FAILED
                return CheckResult.PASSED

        return CheckResult.FAILED


check = HostPort()
