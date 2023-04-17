
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class Ec2TransitGatewayAutoAccept(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-4(21), NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2
        EC2 Transit Gateways should not automatically accept VPC attachment requests
        """
        name = "Ensure Transit Gateways do not automatically accept VPC attachment requests"
        id = "CKV_AWS_331"
        supported_resources = ['aws_ec2_transit_gateway']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'auto_accept_shared_attachments'

    def get_forbidden_values(self):
        return "enable"


check = Ec2TransitGatewayAutoAccept()
