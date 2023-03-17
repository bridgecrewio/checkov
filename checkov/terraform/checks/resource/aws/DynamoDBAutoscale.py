from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DynamoDBAutoscale(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-2(2), NIST.800-53.r5 CP-6(2), NIST.800-53.r5 SC-36,
        NIST.800-53.r5 SC-5(2), NIST.800-53.r5 SI-13(5)
        DynamoDB tables should automatically scale capacity with demand
        """
        name = "Ensure DynamoDB tables automatically scale capacity with demand"
        id = "CKV_AWS_315"
        supported_resources = ['aws_dynamodb_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "billing_mode"

    def get_expected_values(self):
        return ['PAY_PER_REQUEST']


check = DynamoDBAutoscale()
