import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.MSKClusterLogging import check


class TestMSKClusterLogging(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": "test-project",
            "logging_info": [
                {
                    "broker_logs": [
                        {
                            "cloudwatch_logs": [
                                {
                                    "enabled": [False],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_none(self):
        resource_conf = {
            "name": "test-project",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "test-project",
            "logging_info": [
                {
                    "broker_logs": [
                        {
                            "cloudwatch_logs": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_all(self):
        resource_conf = {
            "name": "test-project",
            "logging_info": [
                {
                    "broker_logs": [
                        {
                            "cloudwatch_logs": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        },
                        {
                            "firehose": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        },
                        {
                            "s3": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_mixed(self):
        resource_conf = {
            "name": "test-project",
            "logging_info": [
                {
                    "broker_logs": [
                        {
                            "cloudwatch_logs": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        },
                        {
                            "firehose": [
                                {
                                    "enabled": [True],
                                }
                            ],
                        },
                        {
                            "s3": [
                                {
                                    "enabled": [False],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_empty(self):
        resource_conf = {
            "name": "test-project",
            "logging_info": [
                {
                    "broker_logs": [
                        {
                            "cloudwatch_logs": [
                                {
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
