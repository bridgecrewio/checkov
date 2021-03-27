import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleCloudMySqlLocalInfileOff import check


class TestCloudMySqlLocalInfileOff(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
                resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                  database_version = "MYSQL_8_0"
                  name             = "mysql81"
                  project          = "gcp-bridgecrew-deployment"
                  region           = "us-central1"
                  settings {
                    activation_policy = "ALWAYS"
                    database_flags {
                        name  = "night"
                        value = "on"
                    }
                    database_flags {
                        name  = "local_infile"
                        value = "on"
                    }
                    availability_type = "ZONAL"
                  }
                }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
                        resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                          database_version = "MYSQL_8_0"
                          name             = "general-mysql81"
                          project          = "gcp-bridgecrew-deployment"
                          region           = "us-central1"
                          settings {
                            activation_policy = "ALWAYS"
                            availability_type = "ZONAL"
                            database_flags = [
                                {
                                name = "max_allowed_packet",
                                value = "536870912"
                                },
                                {
                                name  = "local_infile"
                                value = "off"
                                }]
                            pricing_plan     = "PER_USE"
                            replication_type = "SYNCHRONOUS"
                            tier             = "db-n1-standard-1"
                          }
                        }
                        """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads(
            """
                        resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                          database_version = "MYSQL_5_6"
                          name             = "general-mysql81"
                          project          = "gcp-bridgecrew-deployment"
                          region           = "us-central1"

                          settings {
                            activation_policy = "ALWAYS"
                            availability_type = "ZONAL"

                            database_flags {
                              name  = "local_infile"
                              value = "off"
                            }
                            pricing_plan     = "PER_USE"
                            replication_type = "SYNCHRONOUS"
                            tier             = "db-n1-standard-1"
                          }
                        }
                        """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_3(self):
        hcl_res = hcl2.loads(
            """
                        resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                          database_version = "POSTGRES_12"
                          name             = "general-mysql81"
                          project          = "gcp-bridgecrew-deployment"
                          region           = "us-central1"

                          settings {
                            activation_policy = "ALWAYS"
                            availability_type = "ZONAL"
                            database_flags {
                              name  = "local_infilrerege1"
                              value = "off"
                            }
                            database_flags {
                              name  = "local_infile"
                              value = "on"
                            }
                            pricing_plan     = "PER_USE"
                            replication_type = "SYNCHRONOUS"
                            tier             = "db-n1-standard-1"
                          }
                        }
                        """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_4(self):
        hcl_res = hcl2.loads(
            """
                            resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                              database_version = "MYSQL_8_0"
                              name             = "general-mysql81"
                              project          = "gcp-bridgecrew-deployment"
                              region           = "us-central1"

                              settings {
                                activation_policy = "ALWAYS"
                                availability_type = "ZONAL"
                                pricing_plan     = "PER_USE"
                                replication_type = "SYNCHRONOUS"
                                tier             = "db-n1-standard-1"
                              }
                            }
                            """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_5(self):
        hcl_res = hcl2.loads(
            """
                            resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                              database_version = "POSTGRES_12"
                              name             = "general-mysql81"
                              project          = "gcp-bridgecrew-deployment"
                              region           = "us-central1"
                            }
                            """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_6(self):
        hcl_res = hcl2.loads(
            """
                            resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
                              name             = "general-mysql81"
                              project          = "gcp-bridgecrew-deployment"
                              region           = "us-central1"

                              settings {
                                activation_policy = "ALWAYS"
                                availability_type = "ZONAL"
                                pricing_plan     = "PER_USE"
                                replication_type = "SYNCHRONOUS"
                                tier             = "db-n1-standard-1"
                              }
                            }
                            """
        )
        resource_conf = hcl_res["resource"][0]["google_sql_database_instance"][
            "tfer--general-002D-mysql81"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
