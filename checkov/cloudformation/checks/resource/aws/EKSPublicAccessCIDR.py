from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EKSPublicAccessCIDR(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS public endpoint not accessible from 0.0.0.0/0"
        id = "CKV_AWS_38"
        supported_resources = ['AWS::EKS::Cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Check if ResourcesVpcConfig->PublicAccessCidrs allows access from '0.0.0.0/0'
            https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-publicaccesscidrs
        :param conf: AWS::EKS::Cluster configuration
        :return: <CheckResult>
        """
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            vpc_config = properties.get("ResourcesVpcConfig")
            if vpc_config and isinstance(vpc_config, dict):
                # If the public endpoint is disabled, then the CIDR is irrelevant
                endpoint_public_access = vpc_config.get("EndpointPublicAccess")
                if endpoint_public_access and isinstance(endpoint_public_access, bool):
                    if endpoint_public_access is False:
                        return CheckResult.PASSED
                elif endpoint_public_access and isinstance(endpoint_public_access, str):
                    if endpoint_public_access.lower() == "false":
                        return CheckResult.PASSED

                public_access_cidrs = vpc_config.get("PublicAccessCidrs")
                if public_access_cidrs and isinstance(public_access_cidrs, list):
                    # Check if any CIDR allows access from anywhere
                    if "0.0.0.0/0" in public_access_cidrs:
                        return CheckResult.FAILED
                    return CheckResult.PASSED

        # By default, all traffic is allowed
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/ResourcesVpcConfig/EndpointPublicAccess", "Properties/ResourcesVpcConfig/PublicAccessCidrs"]


check = EKSPublicAccessCIDR()
