from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EC2PublicIP(BaseResourceCheck):
    def __init__(self) -> None:
        name = "EC2 instance should not have public IP."
        id = "CKV_AWS_88"
        supported_resources = ('AWS::EC2::Instance', 'AWS::EC2::LaunchTemplate')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('Properties')
        if properties:
            # For AWS::EC2::Instance
            if 'NetworkInterfaces' in properties.keys():
                network_interfaces = properties['NetworkInterfaces']
                if isinstance(network_interfaces, list):
                    for network_interface in network_interfaces:
                        if 'AssociatePublicIpAddress' in network_interface.keys():
                            if network_interface['AssociatePublicIpAddress'] is True:
                                return CheckResult.FAILED
                        else:
                            # If not made explicit then default is true if default subnet and false otherwise.
                            # This info can not be derived from template so result is unknown.
                            # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#Properties%23AssociatePublicIpAddress
                            return CheckResult.UNKNOWN
            # For 'AWS::EC2::LaunchTemplate'
            if 'LaunchTemplateData' in properties.keys():
                if 'NetworkInterfaces' in properties['LaunchTemplateData'].keys():
                    network_interfaces = properties['LaunchTemplateData']['NetworkInterfaces']
                    if isinstance(network_interfaces, list):
                        for network_interface in network_interfaces:
                            if 'AssociatePublicIpAddress' in network_interface.keys():
                                if network_interface['AssociatePublicIpAddress'] is True:
                                    return CheckResult.FAILED
                            else:
                                return CheckResult.UNKNOWN
        return CheckResult.PASSED


check = EC2PublicIP()
