from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.common.util.type_forcers import force_list


class NginxIngressCVE202125742Alias(BaseK8Check):

    def __init__(self):
        name = "Prevent NGINX Ingress annotation snippets which contain alias statements See CVE-2021-25742"
        id = "CKV_K8S_154"
        supported_kind = ['Ingress']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):

        if conf["metadata"]:
            if conf["metadata"].get('annotations'):
                for annotation in force_list(conf["metadata"]["annotations"]):
                    for key, value in annotation.items():
                        if "snippet" in key and "alias" in value:
                            return CheckResult.FAILED
        return CheckResult.PASSED

check = NginxIngressCVE202125742Alias()
