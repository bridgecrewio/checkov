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
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return conf['parent'] + '.image'

    def scan_spec_conf(self, conf):
        if "image" in conf:
            # Split on :
            if ":" in conf["image"]:
                (image, tag) = conf["image"].split(':')
            else:
                image = conf["image"]
                tag = ""
            if tag == "latest" or tag == "":
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = ImageTagFixed()