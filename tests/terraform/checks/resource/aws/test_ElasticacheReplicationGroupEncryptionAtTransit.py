import unittest

from checkov.terraform.checks.resource.aws.ElasticacheReplicationGroupEncryptionAtTransit import check
from checkov.common.models.enums import CheckResult


class TestKMSRotation(unittest.TestCase):

    def test_success(self):
        resource_conf = {'automatic_failover_enabled': [True], 'availability_zones': [['us-west-2a', 'us-west-2b']],
                         'replication_group_id': ['tf-rep-group-1'],
                         'replication_group_description': ['test description'], 'node_type': ['cache.m4.large'],
                         'number_cache_clusters': [2], 'parameter_group_name': ['default.redis3.2'], 'port': [6379],
                         'at_rest_encryption_enabled': [True], 'transit_encryption_enabled': [True],
                         'auth_token': ['${var.auth_token}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {'automatic_failover_enabled': [True], 'availability_zones': [['us-west-2a', 'us-west-2b']],
                         'replication_group_id': ['tf-rep-group-1'],
                         'replication_group_description': ['test description'], 'node_type': ['cache.m4.large'],
                         'number_cache_clusters': [2], 'parameter_group_name': ['default.redis3.2'], 'port': [6379],
                         'at_rest_encryption_enabled': [False], 'transit_encryption_enabled': [False],
                         'auth_token': ['${var.auth_token}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_on_missing_property(self):
        resource_conf = {'automatic_failover_enabled': [True], 'availability_zones': [['us-west-2a', 'us-west-2b']],
                         'replication_group_id': ['tf-rep-group-1'],
                         'replication_group_description': ['test description'], 'node_type': ['cache.m4.large'],
                         'number_cache_clusters': [2], 'parameter_group_name': ['default.redis3.2'], 'port': [6379],

                         'auth_token': ['${var.auth_token}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
