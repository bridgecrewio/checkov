from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EKSNodeGroupRemoteAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Amazon EKS Node group has implict SSH access from 0.0.0.0/0"
        id = "CKV_AWS_100"
        supported_resources = ['aws_eks_node_group']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "remote_access" in conf.keys():
            try:
                if "ec2_ssh_key" in conf["remote_access"][0].keys() and not 'source_security_group_ids' in conf["remote_access"][0].keys():
                    return CheckResult.FAILED
            except:
                return CheckResult.PASSED
        return CheckResult.PASSED


check = EKSNodeGroupRemoteAccess()
