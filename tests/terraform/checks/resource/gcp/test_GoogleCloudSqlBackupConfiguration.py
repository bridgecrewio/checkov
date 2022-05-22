import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudSqlBackupConfiguration import check
from checkov.common.models.enums import CheckResult


class GoogleCloudSqlDatabaseBackupConfiguration(unittest.TestCase):
    def test_failure(self):
        resource_conf = {"name": ["google_cluster"], "monitoring_service": ["none"]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["terraform-master"],
            "region": ["asia-northeasteast1"],
            "database_version": ["MYSQL_5_6"],
            "project": ["test-141901"],
            "settings": [
                {
                    "tier": ["db-f1-micro"],
                    "replication_type": ["SYNCHRONOUS"],
                    "backup_configuration": [{"enabled": [True], "start_time": ["17:00"]}],
                    "ip_configuration": [{"ipv4_enabled": [True]}],
                    "database_flags": [
                        {"name": ["slow_query_log", "character_set_server"], "value": ["on", "utf8mb4"]}
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_replica_unknown(self):
        resource_conf = {"name": ["google_cluster"], "monitoring_service": ["none"], "master_instance_name": "foo"}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)


if __name__ == "__main__":
    unittest.main()
