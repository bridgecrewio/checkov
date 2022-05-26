from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class EKSNodeGroupRemoteAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AWS EKS node group does not have implicit SSH access from 0.0.0.0/0"
        id = "CKV_AWS_100"
        supported_resources = ['aws_eks_node_group']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        remote_access = conf.get("remote_access")
        if remote_access and remote_access[0] and "ec2_ssh_key" in remote_access[0].keys() \
                and "source_security_group_ids" not in remote_access[0].keys():
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['remote_access/[0]/ec2_ssh_key', 'remote_access/[0]/source_security_group_ids']


check = EKSNodeGroupRemoteAccess()
