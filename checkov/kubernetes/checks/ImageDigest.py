from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ImageDigest(BaseK8Check):

    def __init__(self):
        """
        The image specification should use a digest instead of a tag to make sure the container always uses the same
        version of the image.
        https://kubernetes.io/docs/concepts/configuration/overview/#container-images

        An admission controller could be used to enforce the use of image digest
        """
        name = "Image should use digest"
        id = "CKV_K8S_43"
        # Location: container .image
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "image" in conf:

            # The @ indicates there is a digest. It's technically possible to use a tag as well, but it doesn't make
            # a difference. So, this @ is all we need to pass the check.
            image_conf = conf["image"]
            if isinstance(image_conf,str):
                has_digest = '@' in image_conf
                return CheckResult.PASSED if has_digest else CheckResult.FAILED
        else:
            return CheckResult.FAILED


check = ImageDigest()
