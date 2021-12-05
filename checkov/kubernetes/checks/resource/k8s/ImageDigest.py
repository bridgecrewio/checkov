from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ImageDigest(BaseK8sContainerCheck):
    def __init__(self) -> None:
        """
        The image specification should use a digest instead of a tag to make sure the container always uses the same
        version of the image.
        https://kubernetes.io/docs/concepts/configuration/overview/#container-images

        An admission controller could be used to enforce the use of image digest
        """
        name = "Image should use digest"
        id = "CKV_K8S_43"
        # Location: container .image
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["image"]
        if "image" in conf:

            # The @ indicates there is a digest. It's technically possible to use a tag as well, but it doesn't make
            # a difference. So, this @ is all we need to pass the check.
            image_conf = conf["image"]
            if isinstance(image_conf, str):
                has_digest = "@" in image_conf
                return CheckResult.PASSED if has_digest else CheckResult.FAILED
        return CheckResult.FAILED


check = ImageDigest()
