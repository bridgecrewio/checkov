from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.parser.cfn_keywords import ConditionFunctions, IntrinsicFunctions


class ALBListenerHTTPS(BaseResourceCheck):

    def __init__(self):
        name = "Ensure ALB protocol is HTTPS"
        id = "CKV_AWS_2"
        supported_resources = ['AWS::ElasticLoadBalancingV2::Listener']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates ALB protocol is HTTPS
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
        :param conf: aws_alb_listener configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'Protocol' in conf['Properties'].keys():
                if conf['Properties']['Protocol'] in ('HTTPS', 'TLS', 'TCP', 'UDP', 'TCP_UDP'):
                    return CheckResult.PASSED
                else:
                    if isinstance(conf['Properties'].get('DefaultActions', {}), dict):
                        default_actions = conf['Properties'].get('DefaultActions', {}).keys()
                        if any(
                                action in ConditionFunctions.__dict__.values() or action in IntrinsicFunctions.__dict__.values()
                                for action in default_actions):
                            return CheckResult.UNKNOWN
                    if (
                        'DefaultActions' in conf['Properties'].keys()
                        and
                        conf['Properties']['DefaultActions'][0].get('Type') == 'redirect'
                        and
                        conf['Properties']['DefaultActions'][0].get('RedirectConfig', {}).get('Protocol') == "HTTPS"
                    ):
                        return CheckResult.PASSED
        return CheckResult.FAILED

check = ALBListenerHTTPS()
