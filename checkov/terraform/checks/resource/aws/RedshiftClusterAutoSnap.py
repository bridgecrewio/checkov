from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class RedshiftClusterAutoSnap(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6, NIST.800-53.r5 CP-6(1), NIST.800-53.r5 CP-6(2), NIST.800-53.r5 CP-9,
        NIST.800-53.r5 SC-5(2), NIST.800-53.r5 SC-7(10), NIST.800-53.r5 SI-13(5)
        Amazon Redshift clusters should have automatic snapshots enabled
        """
        name = "Ensure Amazon Redshift clusters should have automatic snapshots enabled"
        id = "CKV_AWS_343"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "automated_snapshot_retention_period"

    def get_forbidden_values(self):
        return [0]


check = RedshiftClusterAutoSnap()
