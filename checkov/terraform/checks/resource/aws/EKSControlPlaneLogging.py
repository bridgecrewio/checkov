from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EKSControlPlaneLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS control plane logging enabled for all log types"
        id = "CKV_AWS_37"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for enabled_cluster_log_types at aws_eks_cluster:
            https://www.terraform.io/docs/providers/aws/r/eks_cluster.html
        :param conf: aws_eks_cluster configuration
        :return: <CheckResult>
        """
        if "enabled_cluster_log_types" in conf.keys():
           log_types = [ "api", "audit", "authenticator", "controllerManager", "scheduler" ]

           if all(elem in conf["enabled_cluster_log_types"][0] for elem in log_types):
               return CheckResult.PASSED
           else:
               return CheckResult.FAILED
        else:
           return CheckResult.FAILED
     
check = EKSControlPlaneLogging()

