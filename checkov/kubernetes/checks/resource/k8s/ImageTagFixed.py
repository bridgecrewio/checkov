import re
from typing import Any, Dict

from checkov.common.models.consts import DOCKER_IMAGE_REGEX
from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ImageTagFixed(BaseK8sContainerCheck):
    def __init__(self) -> None:
        """
        You should avoid using the :latest tag when deploying containers in production
        as it is harder to track which version of the image is running
        and more difficult to roll back properly.
        """
        name = "Image Tag should be fixed - not latest or blank"
        id = "CKV_K8S_14"
        # Location: container .image
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["image"]
        if conf.get("image"):

            image_val = conf["image"]
            if not isinstance(image_val, str) or image_val.strip() == "":
                return CheckResult.UNKNOWN

            # If there's a digest, then this is even better than the tag, so the check passes
            if "@" in image_val:
                return CheckResult.PASSED

            (image, tag) = re.findall(DOCKER_IMAGE_REGEX, image_val)[0]
            if tag == "latest" or tag == "":
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = ImageTagFixed()
