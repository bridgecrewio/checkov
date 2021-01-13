import re

from checkov.common.models.consts import DOCKER_IMAGE_REGEX
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ImageTagFixed(BaseK8Check):

    def __init__(self):
        """
        You should avoid using the :latest tag when deploying containers in production
        as it is harder to track which version of the image is running
        and more difficult to roll back properly.
        """
        name = "Image Tag should be fixed - not latest or blank"
        id = "CKV_K8S_14"
        # Location: container .image
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "image" in conf:

            image_val = conf["image"]
            if not isinstance(image_val, str) or image_val.strip() == '':
                return CheckResult.UNKNOWN

            # If there's a digest, then this is even better than the tag, so the check passes
            if '@' in image_val:
                return CheckResult.PASSED

            (image, tag) = re.findall(DOCKER_IMAGE_REGEX, image_val)[0]
            if tag == "latest" or tag == "":
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = ImageTagFixed()
