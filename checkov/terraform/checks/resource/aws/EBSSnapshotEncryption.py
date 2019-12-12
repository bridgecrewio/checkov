from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EBSSnapshotEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS Snapshot is securely encrypted "
        id = "CKV_AWS_4"
        supported_resources = ['aws_ebs_snapshot']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at EBS snapshot:
            https://www.terraform.io/docs/providers/aws/r/ebs_snapshot.html
        :param conf: aws_ebs_snapshot configuration
        :return: <CheckResult>
        """
        if "encrypted" in conf.keys():
            if conf["encrypted"][0] == True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = EBSSnapshotEncryption()
