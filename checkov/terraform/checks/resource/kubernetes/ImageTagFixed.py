from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ImageTagFixed(BaseResourceCheck):

    def __init__(self):
        """
         You should avoid using the :latest tag when deploying containers in production
         as it is harder to track which version of the image is running
         and more difficult to roll back properly.
         """
        name = "Image Tag should be fixed - not latest or blank"
        id = "CKV_K8S_14"
        supported_resources = ["kubernetes_pod"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        if isinstance(spec, dict) and spec.get("container"):
            containers = spec.get("container")
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("image"):
                    name = container.get("image")[0]
                    if ":" in name:
                        if name.split(":")[1] in ("latest", ""):
                            self.evaluated_keys = [f'spec/[0]/container/[{idx}]/image']
                            return CheckResult.FAILED
                        continue
                    if "@" in name:
                        continue
                    self.evaluated_keys = [f'spec/[0]/container/[{idx}]/image']
                    return CheckResult.FAILED
                self.evaluated_keys = [f'spec/[0]/container/[{idx}]']
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = ImageTagFixed()
