from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ECSClusterContainerInsights(BaseResourceCheck):
    def __init__(self):
        name = "Ensure container insights are enabled on ECS cluster"
        id = "CKV_AWS_65"
        supported_resources = ['AWS::ECS::Cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for container insights configuration on ECS cluster:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html#cfn-ecs-cluster-clustersettings
        :param conf: AWS::ECS::Cluster configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'ClusterSettings' in conf['Properties'].keys():
                for setting in conf['Properties']['ClusterSettings']:
                    if setting['Name'] == 'containerInsights' and setting['Value'] == 'enabled':
                        return CheckResult.PASSED
        return CheckResult.FAILED

check = ECSClusterContainerInsights()
