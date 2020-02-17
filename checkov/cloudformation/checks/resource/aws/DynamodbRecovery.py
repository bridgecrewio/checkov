from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_check import BaseResourceCheck


class DynamodbRecovery(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Dynamodb point in time recovery (backup) is enabled"
        id = "CKV_AWS_28"
        supported_resources = ['AWS::DynamoDB::Table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for Point in Time Recovery for DynamoDB Table:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
        :param conf: ddb_table configuration
        :return: <CheckResult>
        """
        if conf['Type'] == 'AWS::DynamoDB::Table':
            if 'Properties' in conf.keys():
                if 'PointInTimeRecoverySpecification' in conf['Properties'].keys():
                    if 'PointInTimeRecoveryEnabled' in conf['Properties']['PointInTimeRecoverySpecification'].keys():
                        if conf['Properties']['PointInTimeRecoverySpecification']['PointInTimeRecoveryEnabled'] == True:
                            return CheckResult.PASSED
        return CheckResult.FAILED

check = DynamodbRecovery()
