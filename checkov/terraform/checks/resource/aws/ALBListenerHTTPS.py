from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ALBListenerHTTPS(BaseResourceCheck):

    def __init__(self):
        name = "Ensure ALB protocol is HTTPS"
        id = "CKV_AWS_2"
        supported_resources = ['aws_lb_listener']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates kms rotation
            https://www.terraform.io/docs/providers/aws/r/lb_listener.html
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        self.evaluated_keys = 'protocol'
        key = 'protocol'
        if key in conf.keys():
            if conf[key] in (["HTTPS"], ["TLS"], ["TCP"], ["UDP"], ["TCP_UDP"]):
                return CheckResult.PASSED
            elif conf[key] == ["HTTP"]:
                if 'default_action' in conf.keys():
                    default_action = conf['default_action'][0]
                    action_type = default_action['type']
                    if action_type == ['redirect']:
                        if default_action.get('redirect'):
                            protocol = default_action['redirect'][0].get('protocol')
                            if protocol == ['HTTPS']:
                                self.evaluated_keys = 'default_action/[0]/redirect/[0]/protocol'
                                return CheckResult.PASSED
                            elif protocol is None:
                                return CheckResult.UNKNOWN
        return CheckResult.FAILED


check = ALBListenerHTTPS()
