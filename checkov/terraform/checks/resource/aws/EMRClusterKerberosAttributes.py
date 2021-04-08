from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterKerberosAttributes(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that EMR clusters have Kerberos Enabled"
        id = "CKV_AWS_114"
        supported_resources = ['aws_emr_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'kerberos_attributes' in conf:
            kerberos_attributes = conf['kerberos_attributes'][0]
            if len(kerberos_attributes) > 0 and 'realm' in kerberos_attributes:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = EMRClusterKerberosAttributes()
