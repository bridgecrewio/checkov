from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list

class ALBListenerTLS12(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Application Load Balancer Listener is using TLS v1.2"
        id = "CKV_AWS_103"
        supported_resources = ['AWS::ElasticLoadBalancingV2::Listener']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates that ALB Listener is using TLS v1.2
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
        :param conf: aws_alb_listener configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'Protocol' in conf['Properties'].keys():
                # Check SslPolicy only if protocol is HTTPS or TLS.
                # Other protocols are not intresting within the context of this check.
                if conf['Properties']['Protocol'] in ('HTTPS', 'TLS'):
                    if 'SslPolicy' in conf['Properties'].keys():
                        if conf['Properties']['SslPolicy'].startswith(("ELBSecurityPolicy-FS-1-2", "ELBSecurityPolicy-TLS-1-2")):
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                elif conf['Properties']['Protocol'] in ('TCP', 'UDP', 'TCP_UDP'):
                        return CheckResult.PASSED
                for idx_action, action in enumerate(conf['Properties']['DefaultActions']):
                    redirects = action.get("RedirectConfig", [])
                    for idx_redirect, redirect in enumerate(force_list(redirects)):
                        if redirect.get("Protocol", []) == 'HTTPS':
                            return CheckResult.PASSED
        return CheckResult.FAILED        

check = ALBListenerTLS12()
