import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.AppLoadBalancerTLS12 import check

class TestAppLoadBalancerTLS12(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'load_balancer_arn': ['${aws_lb.examplea.arn}'], 'port': ['443'], 'protocol': ['HTTPS'], 'ssl_policy': ["ELBSecurityPolicy-2016-08"],
                         'default_action': [{'type': ['forward'], 'target_group_arn': ['${aws_lb_target_group.examplea.arn}'] }]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
 
    def test_success(self):
        resource_conf =  {
            'load_balancer_arn': [
                '${aws_lb.examplea.arn}'
                ], 
            'port': ['443'], 
            'protocol': ['HTTPS'], 
            'ssl_policy': ["ELBSecurityPolicy-TLS-1-2-2017-01"],
            'default_action': [
                {
                    'type': ['forward'], 
                    'target_group_arn': [
                        '${aws_lb_target_group.examplea.arn}'
                ]
            }
        ]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_redirect(self):
        hcl_res = hcl2.loads("""
            resource "aws_lb_listener" "http" {
              load_balancer_arn = aws_lb.public.arn
              port              = "80"
              protocol          = "HTTP" 
            
              default_action {
                redirect {
                  port        = "443"
                  protocol    = "HTTPS"
                  status_code = "HTTP_301"
                }
                type = "redirect"
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['aws_lb_listener']['http']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()

