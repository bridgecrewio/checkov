from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubernetesDashboard(BaseK8Check):

    def __init__(self):
        name = "Ensure the Kubernetes dashboard is not deployed"
        id = "CKV_K8S_33"
        # Location: container .image
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "image" in conf:
            conf_image = conf["image"]
            if not isinstance(conf_image, str):
                return CheckResult.FAILED
            if ("kubernetes-dashboard" in conf_image or "kubernetesui" in conf_image):
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        if "parent_metadata" in conf:
            if conf["parent_metadata"].get("labels"):
                if "app" in conf["parent_metadata"]["labels"]:
                    if conf["parent_metadata"]["labels"]["app"] == "kubernetes-dashboard":
                        return CheckResult.FAILED
                elif "k8s-app" in conf["parent_metadata"]["labels"]:
                    if conf["parent_metadata"]["labels"]["k8s-app"] == "kubernetes-dashboard":
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = KubernetesDashboard()
