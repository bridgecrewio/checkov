from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3BucketReplicationConfiguration(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that S3 bucket has cross-region replication enabled"
        id = "CKV_AWS_144"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "replication_configuration/[0]/role"

    def get_expected_value(self):
        return ANY_VALUE


check = S3BucketReplicationConfiguration()
