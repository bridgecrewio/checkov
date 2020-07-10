from checkov.common.models.enums import CheckCategories
from checkov.kubernetes.base_spec_omitted_or_value_check import BaseSpecOmittedOrValueCheck


class ShareHostPIDPSP(BaseSpecOmittedOrValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.2
        # CIS-1.5 5.2.2
        name = "Do not admit containers wishing to share the host process ID namespace"
        id = "CKV_K8S_1"
        # Location: PodSecurityPolicy.spec.hostPID
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_inspected_key(self):
        return "spec/hostPID"

    def get_resource_id(self, conf):
        if "metadata" in conf:
            if "name" in conf["metadata"]:
                return 'PodSecurityPolicy.{}'.format(conf["metadata"]["name"])
        return 'PodSecurityPolicy.spec.hostPID'


check = ShareHostPIDPSP()
