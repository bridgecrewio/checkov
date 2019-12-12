from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EBSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS is securely encrypted "
        id = "CKV_AWS_3"
        supported_resources = ['aws_ebs_volume']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at ebs volume:
            https://www.terraform.io/docs/providers/aws/r/ebs_volume.html
        :param conf: ebs_volume configuration
        :return: <CheckResult>
        """
        if "encrypted" in conf.keys():
            if conf["encrypted"][0] == True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = EBSEncryption()
