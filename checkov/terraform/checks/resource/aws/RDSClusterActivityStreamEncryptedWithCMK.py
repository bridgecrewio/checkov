from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class RDSClusterActivityStreamEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RDS Cluster activity streams are encrypted using KMS CMKs"
        id = "CKV_AWS_246"
        supported_resources = ['aws_rds_cluster_activity_stream']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for encryption configuration for cluster activity streams:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/rds_cluster_activity_stream
        :param conf: aws_rds_cluster_activity_stream
        :return: <CheckResult>
        """
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = RDSClusterActivityStreamEncryptedWithCMK()
