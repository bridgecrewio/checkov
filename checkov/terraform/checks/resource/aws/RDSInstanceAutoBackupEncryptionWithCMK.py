from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class RDSInstanceAutoBackupEncryptionWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure replicated backups are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_245"
        supported_resources = ['aws_db_instance_automated_backups_replication']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for encryption configuration for backup replication:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance_automated_backups_replication
        :param conf: aws_db_instance_automated_backups_replication configuration
        :return: <CheckResult>
        """
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = RDSInstanceAutoBackupEncryptionWithCMK()
