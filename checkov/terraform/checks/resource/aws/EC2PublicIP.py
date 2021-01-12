from checkov.common.models.enums import (
    CheckCategories,
    CheckResult,
)
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EC2PublicIP(BaseResourceCheck):

    def __init__(self):
        name = "EC2 instance should not have public IP."
        id = "CKV_AWS_88"
        categories = [CheckCategories.NETWORKING]
        supported_resources = ['aws_instance', 'aws_launch_template']
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        """
        Looks for if associate_public_ip_address is set
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#associate_public_ip_address
            or
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_template#associate_public_ip_address

        :param conf: dict of supported resource configuration
        :return: <CheckResult>
        """
        # For aws_instance
        if 'associate_public_ip_address' in conf.keys():
            self.evaluated_keys = 'associate_public_ip_address'
            if conf['associate_public_ip_address'] == [True]:
                return CheckResult.FAILED

        # For aws_launch_template
        if 'network_interfaces' in conf and isinstance(conf['network_interfaces'][0], dict):
            self.evaluated_keys = 'network_interfaces/[0]/associate_public_ip_address'
            if 'associate_public_ip_address' in conf['network_interfaces'][0]:
                if conf['network_interfaces'][0]['associate_public_ip_address'] == [True]:
                    return CheckResult.FAILED

        # Note: checkov does not know, so we default to PASSED
        # There is no default value for associate_public_ip_address, it depends on the subnet
        return CheckResult.PASSED

check = EC2PublicIP()
