from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class Tiller(BaseK8Check):

    def __init__(self):
        name = "Ensure that Tiller (Helm v2) is not deployed"
        id = "CKV_K8S_34"
        # Location: container .image
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        return CheckResult.FAILED if self.is_tiller(conf) else CheckResult.PASSED

    @staticmethod
    def is_tiller(conf):
        if "image" in conf:
            conf_image = conf["image"]
            if isinstance(conf_image,str) and  "tiller" in conf_image:
                    return True

        if "parent_metadata" in conf:
            if "labels" in conf["parent_metadata"]:
                if "app" in conf["parent_metadata"]["labels"]:
                    if conf["parent_metadata"]["labels"]["app"] == "helm":
                        return True
                elif "name" in conf["parent_metadata"]["labels"]:
                    if conf["parent_metadata"]["labels"]["name"] == "tiller":
                        return True

        return False

check = Tiller()