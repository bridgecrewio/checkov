import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.yandexcloud.MDBSecurityGroup import check
from checkov.terraform.runner import Runner

class TestMDBSecurityGroup(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_MDBSecurityGroup"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'yandex_mdb_postgresql_cluster.pass',
            'yandex_mdb_sqlserver_cluster.pass',
            'yandex_mdb_redis_cluster.pass',
            'yandex_mdb_mysql_cluster.pass',
            'yandex_mdb_mongodb_cluster.pass',
            'yandex_mdb_kafka_cluster.pass',
            'yandex_mdb_greenplum_cluster.pass',
            'yandex_mdb_elasticsearch_cluster.pass',
            'yandex_mdb_clickhouse_cluster.pass',
        }
        failing_resources = {
            'yandex_mdb_postgresql_cluster.fail',
            'yandex_mdb_sqlserver_cluster.fail',
            'yandex_mdb_redis_cluster.fail',
            'yandex_mdb_mysql_cluster.fail',
            'yandex_mdb_mongodb_cluster.fail',
            'yandex_mdb_kafka_cluster.fail',
            'yandex_mdb_greenplum_cluster.fail',
            'yandex_mdb_elasticsearch_cluster.fail',
            'yandex_mdb_clickhouse_cluster.fail',
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 9)
        self.assertEqual(summary["failed"], 9)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == "__main__":
    unittest.main()
