from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class Secrets(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.4.1
        name = "Prefer using secrets as files over secrets as environment variables"
        id = "CKV_K8S_35"

        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]
        containers = spec.get("container")
        if containers:

            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN

                if container.get("env") and isinstance(container.get("env"), list):
                    env = container.get("env")[0]
                    for idy, e in enumerate(env):
                        if "value_from" in e:
                            if isinstance(env.get("value_from"), list):
                                value_from = env.get("value_from")[0]
                                if value_from.get("secret_key_ref"):
                                    self.evaluated_keys = \
                                        [f"spec/[0]/container/[{idx}]/env/[{idy}]/value_from/secret_key_ref"]
                                    return CheckResult.FAILED
                if container.get("env_from") and isinstance(container.get("env_from"), list):
                    env_from = container.get("env_from")[0]
                    for idy, ef in enumerate(env_from):
                        if "secret_ref" in ef:
                            self.evaluated_keys = \
                                [f"spec/[0]/container/[{idx}]/env_from/[{idy}]/secret_ref"]
                            return CheckResult.FAILED
            return CheckResult.PASSED


check = Secrets()
