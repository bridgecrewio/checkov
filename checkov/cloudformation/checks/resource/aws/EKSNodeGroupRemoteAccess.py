from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class EKSNodeGroupRemoteAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AWS EKS node group does not have implicit SSH access from 0.0.0.0/0"
        id = "CKV_AWS_100"
        supported_resources = ['AWS::EKS::Nodegroup']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'RemoteAccess' in conf['Properties'].keys():
                if 'Ec2SshKey' in conf['Properties']['RemoteAccess'].keys():
                    if 'SourceSecurityGroups' in conf['Properties']['RemoteAccess'].keys():
                        return CheckResult.PASSED
                    else:
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/RemoteAccess/Ec2SshKey", "Properties/RemoteAccess/SourceSecurityGroups"]


check = EKSNodeGroupRemoteAccess()
