import unittest


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

if __name__ == '__main__':
    unittest.main()

