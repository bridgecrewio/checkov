import unittest
import hcl2

from checkov.terraform.checks.resource.gcp.GoogleCloudSqlDatabasePublicallyAccessible import check
from checkov.common.models.enums import CheckResult


class GoogleCloudSqlDatabasePublicallyAccessible(unittest.TestCase):

    def test_failure(self):
        hcl_parsed = hcl2.loads("""
resource google_sql_database_instance "master_instance" {
  name             = "terragoat-${var.environment}-master"
  database_version = "POSTGRES_11"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "WWW"
        value = "0.0.0.0/0"
      }
    }
  }
}
""")
        resource_conf = hcl_parsed['resource'][0]['google_sql_database_instance']['master_instance']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'settings': [{'tier': ['db-f1-micro'], 'ip_configuration': [{'ipv4_enabled': True, 'authorized_networks': [ {'name': 'net1', 'value': '10.0.0.0/16'}, {'name': 'net1', 'value': '10.10.0.0/16'} ]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown(self):
            hcl_parsed = hcl2.loads("""
    resource "google_sql_database_instance" "sql_instance" {
      name   = "${var.gcp-project}-db-dev"
      region = "${var.region}"
      settings {
        tier = "${var.db_machine_type}"
        ip_configuration {
                    ipv4_enabled = true
                    authorized_networks {
                    name = "${var.gcp-project}-sql-network"
                    value = google_compute_address.ip_address-dev.address
                    }
      }
     }
    }""")
            resource_conf = hcl_parsed['resource'][0]['google_sql_database_instance']['sql_instance']
            scan_result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
