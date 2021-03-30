import unittest
import hcl2

from checkov.terraform.checks.resource.aws.ElasticCacheAutomaticBackup import check
from checkov.common.models.enums import CheckResult


class TestElasticCacheAutomaticBackup(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_elasticache_cluster" "example" {
                  cluster_id           = "cluster-example"
                  engine               = "redis"
                  node_type            = "cache.m4.large"
                  num_cache_nodes      = 1
                  parameter_group_name = "default.redis3.2"
                  engine_version       = "3.2.10"
                  port                 = 6379
                  snapshot_retention_limit = 0
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elasticache_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure1(self):
        hcl_res = hcl2.loads("""
                resource "aws_elasticache_cluster" "example" {
                  cluster_id           = "cluster-example"
                  engine               = "redis"
                  node_type            = "cache.m4.large"
                  num_cache_nodes      = 1
                  parameter_group_name = "default.redis3.2"
                  engine_version       = "3.2.10"
                  port                 = 6379
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elasticache_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_elasticache_cluster" "example" {
                  cluster_id           = "cluster-example"
                  engine               = "redis"
                  node_type            = "cache.m4.large"
                  num_cache_nodes      = 1
                  parameter_group_name = "default.redis3.2"
                  engine_version       = "3.2.10"
                  port                 = 6379
                  snapshot_retention_limit = 5
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elasticache_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
