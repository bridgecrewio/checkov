import json
import unittest
from unittest.mock import patch

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.scanners.S3AccessLogs import S3AccessLogsScanner


class TestS3AccessLogs(unittest.TestCase):

    def test_failure_s3_accesslogs(self):
        scanner = S3AccessLogsScanner()
        resource_conf = {"region": ["us-west-2"],
                         "bucket": ["my_bucket"],
                         "acl": ["public-read"],
                         "force_destroy": [True],
                         "tags": [{"Name": "my-bucket"}]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success_s3_accesslogs(self):
        scanner = S3AccessLogsScanner()

        resource_conf = {"region": ["us-west-2"],
                         "bucket": ["my_bucket"],
                         "acl": ["public-read"],
                         "force_destroy": [True],
                         "tags": [{"Name": "my-bucket"}],
                         "logging": [{"target_bucket": "logging-bucket",
                                      "target_prefix": "log/"
                                      }]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
