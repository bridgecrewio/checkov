from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ImagePullPolicyAlways(BaseK8Check):

    def __init__(self):
        """
        Image pull policy should be set to always to ensure you get the correct image and imagePullSecrets are correct
        Default is 'IfNotPresent' unless image tag is omitted or :latest
        https://kubernetes.io/docs/concepts/configuration/overview/#container-images

        An admission controller could be used to enforce imagePullPolicy
        """
        name = "Image Pull Policy should be Always"
        id = "CKV_K8S_15"
        # Location: container .imagePullPolicy
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return conf['parent']

    def scan_spec_conf(self, conf):
        if "image" in conf:
            
            # Remove the digest, if present
            image_val = conf["image"]
            if '@' in image_val:
                image_val = image_val[0:image_val.index('@')]

            # Split on :
            if ":" in image_val:
                (image, tag) = image_val.split(':')
            else:
                image = image_val
                tag = ""
            if "imagePullPolicy" not in conf:
                if tag == "latest" or tag == "":
                    # Default imagePullPolicy = Always
                    return CheckResult.PASSED
                else:
                    # Default imagePullPolicy = IfNotPresent
                    return CheckResult.FAILED
            else:
                if conf["imagePullPolicy"] != "Always":
                    return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = ImagePullPolicyAlways()