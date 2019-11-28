from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner
from bridgecrew.terraformscanner.resource_scanners.aws.ALBListenerHTTPS import ALBListenerHTTPS


class LBListenerHTTPS(ALBListenerHTTPS):
    def __init__(self):
        name = "Ensure ALB protocol is HTTPS"
        scan_id = "BC_AWS_ENCRYPTION_8"
        supported_resource = 'aws_lb_listener'
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        return super().scan_resource_conf(conf)


scanner = LBListenerHTTPS()
