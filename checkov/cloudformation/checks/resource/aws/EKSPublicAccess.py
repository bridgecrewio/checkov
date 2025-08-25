from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EKSPublicAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS public endpoint is disabled"
        id = "CKV_AWS_39"
        supported_resources = ['AWS::EKS::Cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Checks the EndpointPublicAccess property of the AWS::EKS::Cluster resource:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-endpointpublicaccess
        :param conf: AWS::EKS::Cluster configuration
        :return: <CheckResult>
        """
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            vpc_config = properties.get("ResourcesVpcConfig")
            if vpc_config and isinstance(vpc_config, dict):
                endpoint_public_access = vpc_config.get("EndpointPublicAccess")
                if endpoint_public_access and isinstance(endpoint_public_access, bool):
                    if endpoint_public_access is False:
                        return CheckResult.PASSED
                elif endpoint_public_access and isinstance(endpoint_public_access, str):
                    if endpoint_public_access.lower() == "false":
                        return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/ResourcesVpcConfig/EndpointPublicAccess"]


check = EKSPublicAccess()
