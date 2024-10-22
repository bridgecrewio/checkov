from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class RedshiftClusterUseEnhancedVPCRouting(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-4, NIST.800-53.r5 AC-4(21), NIST.800-53.r5 SC-7,
        NIST.800-53.r5 SC-7(11), NIST.800-53.r5 SC-7(20),
        NIST.800-53.r5 SC-7(21), NIST.800-53.r5 SC-7(4), NIST.800-53.r5 SC-7(9)
        Redshift clusters should use enhanced VPC routing
        """
        name = "Ensure Redshift clusters use enhanced VPC routing"
        id = "CKV_AWS_321"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "enhanced_vpc_routing"


check = RedshiftClusterUseEnhancedVPCRouting()
