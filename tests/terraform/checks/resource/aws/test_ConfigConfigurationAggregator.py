import unittest
import hcl2

from checkov.terraform.checks.resource.aws.ConfigConfgurationAggregatorAllRegions import check
from checkov.common.models.enums import CheckResult


class TestConfigConfigurationAggregator(unittest.TestCase):

    def test_failure_account(self):
        hcl_res = hcl2.loads("""
                    resource "aws_config_configuration_aggregator" "organization" {
                    
                      name = "example"
                    
                      account_aggregation_source {
                        account_ids = ["123456789012"]
                        regions     = ["us-east-2", "us-east-1", "us-west-1", "us-west-2"]
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_config_configuration_aggregator']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_organization(self):
        hcl_res = hcl2.loads("""
                    resource "aws_config_configuration_aggregator" "organization" {
                    
                      name = "example"
                    
                      organization_aggregation_source {
                        role_arn    = aws_iam_role.organization.arn
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_config_configuration_aggregator']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_config_configuration_aggregator" "organization" {
                    
                      name = "example"
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_config_configuration_aggregator']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_account(self):
        hcl_res = hcl2.loads("""
                    resource "aws_config_configuration_aggregator" "organization" {
                    
                      name = "example"
                    
                      account_aggregation_source {
                        account_ids  = ["123456789012"]
                        all_regions  = true
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_config_configuration_aggregator']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_organization(self):
        hcl_res = hcl2.loads("""
                    resource "aws_config_configuration_aggregator" "organization" {
                    
                      name = "example"
                    
                      organization_aggregation_source {
                        all_regions = true
                        role_arn    = aws_iam_role.organization.arn
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_config_configuration_aggregator']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
