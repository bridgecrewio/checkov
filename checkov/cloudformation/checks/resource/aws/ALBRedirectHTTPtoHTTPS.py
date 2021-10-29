from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list

class ALBRedirectHTTPtoHTTPS(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Application Load Balancer is redirecting HTTP to HTTPS"
        id = "CKV_AWS_175"
        supported_resources = ['AWS::ElasticLoadBalancingV2::Listener']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates ALB Listener is redirecting HTTP to HTTPS
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
        :param conf: aws_alb_listener configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'Port' in conf['Properties'].keys():
                if conf['Properties']['Port'] == 80 and conf['Properties']['Protocol'] == 'HTTP':
                    for idx_action, action in enumerate(conf['Properties']['DefaultActions']):
                        redirects = action.get("RedirectConfig", [])
                        if redirects:
                            for idx_redirect, redirect in enumerate(force_list(redirects)):
                                # We're interested in 'Protocol' spesifically when type is 'redirect'.' If 'Protocol' is not spesified 
                                # in the redirect rule then it defaults to the original request protocol (HTTP in this case)
                                if redirect.get("Protocol", []) == 'HTTPS' and action.get("Type", []) == 'redirect' and redirect.get("Port", []) == 443:
                                    return CheckResult.PASSED
                                else:
                                    return CheckResult.FAILED  
                        else:
                            # HTTP/80 and no redirect so failure
                            return CheckResult.FAILED  
                else:
                    return CheckResult.PASSED                               

check = ALBRedirectHTTPtoHTTPS()
