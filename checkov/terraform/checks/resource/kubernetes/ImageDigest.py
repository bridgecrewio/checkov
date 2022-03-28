
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ImageDigest(BaseResourceCheck):

    def __init__(self):
        """
         The image specification should use a digest instead of a tag to make sure the container always uses the same
         version of the image.
         https://kubernetes.io/docs/concepts/configuration/overview/#container-images

         An admission controller could be used to enforce the use of image digest
         """
        name = "Image should use digest"
        id = "CKV_K8S_43"
        supported_resources = ["kubernetes_pod"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec')[0]
        if spec:
            containers = spec.get("container")
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("image") and isinstance(container.get("image"), list):
                    name = container.get("image")[0]
                    if "@" not in name:
                        self.evaluated_keys = [f'spec/[0]/container/[{idx}]/image']
                        return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = ImageDigest()
