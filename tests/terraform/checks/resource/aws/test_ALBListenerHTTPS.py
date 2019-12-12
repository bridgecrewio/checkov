import unittest

from checkov.terraform.checks.resource.aws.ALBListenerHTTPS import check
from checkov.terraform.models.enums import CheckResult


class TestALBListenerHTTPS(unittest.TestCase):

    def test_success_redirect(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP'],
                         'default_action': [{'type': ['redirect'], 'redirect': [
                             {'port': ['443'], 'protocol': ['HTTPS'], 'status_code': ['HTTP_301']}]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['443'], 'protocol': ['HTTPS']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
