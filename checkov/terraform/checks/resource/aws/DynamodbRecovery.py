from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class DynamodbRecovery(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Dynamodb point in time recovery (backup) is enabled"
        id = "CKV_AWS_28"
        supported_resources = ['aws_dynamodb_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at ebs volume:
            https://www.terraform.io/docs/providers/aws/r/ebs_volume.html
        :param conf: ebs_volume configuration
        :return: <CheckResult>
        """
        if "point_in_time_recovery" in conf.keys():
            if conf["point_in_time_recovery"][0]['enabled'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = DynamodbRecovery()
