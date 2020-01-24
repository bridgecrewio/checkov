from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck

class EKSPublicAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS public endpoint disabled"
        id = "CKV_AWS_39"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for endpoint_public_access disabled at aws_eks_cluster:
            https://www.terraform.io/docs/providers/aws/r/eks_cluster.html
        :param conf: aws_eks_cluster configuration
        :return: <CheckResult>
        """
        if "vpc_config" in conf.keys():
           if "endpoint_public_access" in conf["vpc_config"][0].keys():
               if conf["vpc_config"][0]["endpoint_public_access"][0] == False:
                   return CheckResult.PASSED
               else:
                   return CheckResult.FAILED
           else: 
               return CheckResult.FAILED
        else:
           return CheckResult.UNKNOWN
     
check = EKSPublicAccess()

