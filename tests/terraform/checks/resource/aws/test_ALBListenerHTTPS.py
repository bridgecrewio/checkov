import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ALBListenerHTTPS import check


class TestALBListenerHTTPS(unittest.TestCase):

    def test_success_redirect(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP'],
                         'default_action': [{'type': ['redirect'], 'redirect': [
                             {'port': ['443'], 'protocol': ['HTTPS'], 'status_code': ['HTTP_301']}]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_1(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['443'], 'protocol': ['HTTPS']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        resource_conf = {'load_balancer_arn': ['${aws_alb.front_end.arn}'], 'port': ['443'], 'protocol': ['HTTPS']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_nlb_tcp_success(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['22'], 'protocol': ['TCP']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_nlb_udp_success(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['53'], 'protocol': ['UDP']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_nlb_tcp_udp_success(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['53'], 'protocol': ['TCP_UDP']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_1(self):
        resource_conf = {'load_balancer_arn': ['${aws_lb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        resource_conf = {'load_balancer_arn': ['${aws_alb.front_end.arn}'], 'port': ['80'], 'protocol': ['HTTP']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_no_protocol(self):
        hcl_res = hcl2.loads("""
resource "aws_lb_listener" "http_redirector" {
  load_balancer_arn = aws_lb.redirector.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect {
      host        = "example.com"
      status_code = "HTTP_302"
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_lb_listener']['http_redirector']
        result = check.scan_resource_conf(resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, result)

    def test_unknown_not_rendered(self):
        hcl_res = hcl2.loads("""
resource "aws_lb_listener" "http_redirector" {
  load_balancer_arn = aws_lb.redirector.arn
  port              = "80"
  protocol          = var.lb_protocol
  default_action {
    type = "redirect"
    redirect {
      host        = "example.com"
      status_code = "HTTP_302"
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_lb_listener']['http_redirector']
        result = check.scan_resource_conf(resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, result)


if __name__ == '__main__':
    unittest.main()
