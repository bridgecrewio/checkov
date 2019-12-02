import unittest

from checkov.terraformscanner.models.enums import ScanResult
from checkov.terraformscanner.resource_scanners.aws.ALBListenerHTTPS import scanner


class TestALBListenerHTTPS(unittest.TestCase):

    def test_success_redirect(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP'],
                         'default_action': [{'type': ['redirect'], 'redirect': [
                             {'port': ['443'], 'protocol': ['HTTPS'], 'status_code': ['HTTP_301']}]}]}

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

    def test_success(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['443'], 'protocol': ['HTTPS']}

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

    def test_failure(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP']}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)


if __name__ == '__main__':
    unittest.main()
