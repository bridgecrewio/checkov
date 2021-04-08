import unittest

from checkov.terraform.checks.resource.aws.ElasticsearchInVPC import check
from checkov.common.models.enums import CheckResult

import hcl2


class TestElasticsearchInVPC(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "aws_elasticsearch_domain" "es" {
          domain_name           = var.domain
          elasticsearch_version = "6.3"
        
          cluster_config {
            instance_type = "m4.large.elasticsearch"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elasticsearch_domain']['es']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_elasticsearch_domain" "es" {
          domain_name           = var.domain
          elasticsearch_version = "6.3"
        
          cluster_config {
            instance_type = "m4.large.elasticsearch"
          }
        
          vpc_options {
            subnet_ids = [
              data.aws_subnet_ids.selected.ids[0],
              data.aws_subnet_ids.selected.ids[1],
            ]
        
            security_group_ids = [aws_security_group.es.id]
          }
        
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elasticsearch_domain']['es']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
