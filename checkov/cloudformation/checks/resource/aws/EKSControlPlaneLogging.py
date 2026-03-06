from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EKSControlPlaneLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS control plane logging enabled for all log types"
        id = "CKV_AWS_37"
        supported_resources = ['AWS::EKS::Cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for the configured logging types at AWS::EKS::Cluster:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-eks-cluster.html#cfn-eks-cluster-logging
        :param conf: AWS::EKS::Cluster configuration
        :return: <CheckResult>
        """
        log_types = ["api", "audit", "authenticator",
                     "controllerManager", "scheduler"]

        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            logging = properties.get("Logging")
            if logging and isinstance(logging, dict):
                cluster_logging = logging.get("ClusterLogging")
                if cluster_logging and isinstance(cluster_logging, dict):
                    enabled_types = cluster_logging.get("EnabledTypes")
                    if enabled_types and isinstance(enabled_types, list):
                        # This normalizes the type, as either a dict or a list of strings could be passed down to `EnabledTypes`
                        normalized: list[str] = []
                        for t in enabled_types:
                            if isinstance(t, str):
                                normalized.append(t)
                            elif isinstance(t, dict):
                                type_value = t.get("Type")
                                if isinstance(type_value, str):
                                    normalized.append(type_value)

                        if all(elem in normalized for elem in log_types):
                            return CheckResult.PASSED
        
        # By default, no logging is enabled
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/Logging/ClusterLogging/EnabledTypes"]


check = EKSControlPlaneLogging()