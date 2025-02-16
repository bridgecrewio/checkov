import unittest

import hcl2

from checkov.terraform.checks.resource.aws.ECSClusterContainerInsights import check
from checkov.common.models.enums import CheckResult


class TestECSClusterContainerInsights(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_ecs_cluster" "my_cluster" {
                name = "white-hart"
            }
            """
        )
        resource_conf = hcl_res['resource'][0]['aws_ecs_cluster']['my_cluster']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_explicit_disable(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_ecs_cluster" "my_cluster" {
                name = "white-hart"
                setting {
                    name = "containerInsights"
                    value = "disabled"
                }
            }
            """
        )
        resource_conf = hcl_res['resource'][0]['aws_ecs_cluster']['my_cluster']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_ecs_cluster" "my_cluster" {
                name = "white-hart"
                setting {
                    name = "containerInsights"
                    value = "enabled"
                }
            }
            """
        )
        resource_conf = hcl_res['resource'][0]['aws_ecs_cluster']['my_cluster']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_enhanced(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_ecs_cluster" "my_cluster" {
                name = "white-hart"
                setting {
                    name = "containerInsights"
                    value = "enhanced"
                }
            }
            """
        )
        resource_conf = hcl_res['resource'][0]['aws_ecs_cluster']['my_cluster']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
