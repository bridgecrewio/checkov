from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class ALBListenerHTTPS(ResourceScanner):

    def __init__(self,name="", scan_id="", categories="", supported_resource=""):
        name = "Ensure ALB protocol is HTTPS"
        scan_id = "BC_AWS_ENCRYPTION_8"
        if not supported_resource:
            supported_resource = 'aws_alb_listener'
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            validates kms rotation
            https://www.terraform.io/docs/providers/aws/r/lb_listener.html
        :param conf: aws_kms_key configuration
        :return: <ScanResult>
        """
        key = 'protocol'
        if key in conf.keys():
            if conf[key] == ["HTTPS"]:
                return ScanResult.SUCCESS
            elif conf[key] == ["HTTP"]:
                if 'default_action' in conf.keys():
                    default_action = conf['default_action'][0]
                    action_type = default_action['type']
                    if action_type == ['redirect']:
                        if default_action['redirect'][0]['protocol'] == ['HTTPS']:
                            return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = ALBListenerHTTPS()
