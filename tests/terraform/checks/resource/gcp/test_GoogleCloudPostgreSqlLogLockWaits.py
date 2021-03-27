import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleCloudPostgreSqlLogLockWaits import (
    check,
)


class TestCloudPostgreSQLLogLockWaits(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "google_sql_database_instance" "tfer--general-002D-pos121" {
              database_version = "POSTGRES_12"
              name             = "general-pos121"
              project          = "gcp-bridgecrew-deployment"
              region           = "us-central1"
              settings {
                activation_policy = "ALWAYS"
                availability_type = "ZONAL"
                database_flags =[{
                  name  = "log_checkpoints"
                  value = "on"
                },{
                  name  = "log_connections"
                  value = "on"
                }, {
                  name  = "log_disconnections"
                  value = "off"
                }, {
                  name  = "log_min_messages"
                  value = "debug6"
                }, {
                  name  = "log_lock_waits"
                  value = "off"
                }, {
                  name  = "log_temp_files"
                  value = "10"
                },{
                  name  = "log_min_duration_statement"
                  value = "1"
                }]
                pricing_plan     = "PER_USE"
                replication_type = "SYNCHRONOUS"
                tier             = "db-custom-1-3840"
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-pos121"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "google_sql_database_instance" "tfer--general-002D-pos121" {
            database_version = "POSTGRES_12"
            name             = "general-pos121"
            project          = "gcp-bridgecrew-deployment"
            region           = "us-central1"
            settings {
                activation_policy = "ALWAYS"
                availability_type = "ZONAL"
                database_flags {
                  name  = "log_checkpoints"
                  value = "off"
                }
                database_flags {
                  name  = "log_connections"
                  value = "on"
                }
                database_flags {
                  name  = "log_disconnections"
                  value = "on"
                }
                database_flags {
                  name  = "log_min_messages"
                  value = "debug6"
                }
                database_flags {
                  name  = "log_lock_waits"
                  value = "on"
                }
                database_flags {
                  name  = "log_temp_files"
                  value = "10"
                }
                database_flags {
                  name  = "log_min_duration_statement"
                  value = "1"
                }
                pricing_plan     = "PER_USE"
                replication_type = "SYNCHRONOUS"
                tier             = "db-custom-1-3840"
              }
            }
                        """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-pos121"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_3(self):
        hcl_res = hcl2.loads(
            """
                                    resource "google_sql_database_instance" "tfer--general-002D-pos121" {
            database_version = "POSTGRES_12"
            name             = "general-pos121"
            project          = "gcp-bridgecrew-deployment"
            region           = "us-central1"
            settings {
                activation_policy = "ALWAYS"
                availability_type = "ZONAL"
                database_flags {
                  name  = "log_min_messages"
                  value = "debug6"
                }
                database_flags {
                  name  = "log_temp_files"
                  value = "10"
                }
                database_flags {
                  name  = "log_min_duration_statement"
                  value = "1"
                }
                pricing_plan     = "PER_USE"
                replication_type = "SYNCHRONOUS"
                tier             = "db-custom-1-3840"
              }
            }
                        """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-pos121"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
