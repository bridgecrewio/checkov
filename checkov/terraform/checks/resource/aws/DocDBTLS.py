from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class DocDBTLS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DocDB TLS is not disabled"
        id = "CKV_AWS_90"
        supported_resources = ['aws_docdb_cluster_parameter_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'parameter' in conf:
            for elem in conf["parameter"]:
                if isinstance(elem, dict) and elem["name"][0] == "tls" and elem["value"][0] == "disabled":
                    return CheckResult.FAILED
        else:
            return CheckResult.PASSED
        return CheckResult.PASSED


check = DocDBTLS()
