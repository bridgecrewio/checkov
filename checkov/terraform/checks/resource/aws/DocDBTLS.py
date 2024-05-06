from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class DocDBTLS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DocumentDB TLS is not disabled"
        id = "CKV_AWS_90"
        supported_resources = ['aws_docdb_cluster_parameter_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['parameter']
        if 'parameter' in conf:
            for idx, elem in enumerate(conf["parameter"]):
                if isinstance(elem, dict) and elem["name"][0] == "tls" and elem["value"][0] == "disabled":
                    self.evaluated_keys = [f'parameter/[{idx}]/name', f'parameter/[{idx}]/value']
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = DocDBTLS()
