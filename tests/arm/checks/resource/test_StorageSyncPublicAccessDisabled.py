import os
import unittest
from checkov.arm.checks.resource.StorageSyncPublicAccessDisabled import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.common.models.enums import CheckResult


class TestStorageSyncPublicAccessDisabled(unittest.TestCase):
    def test_failure_1(self):
        resource_conf = {
            "type": "Microsoft.StorageSync/storageSyncServices",
            "apiVersion": "2021-02-01",
            "name": "example-storage-sync",
            "properties": {
                "storageSyncServiceStatus": "Registered",
                "storageSyncServiceProperties": {
                    "trustState": "Enabled",
                    "storageSyncServiceUid": "65fdd65b-ea5d-4a00-bf7f-40c41ba39ae4",
                    "provisioningState": "Succeeded"
                },
                "location": "East US",
                "tags": {
                    "foo": "bar"
                }
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

        def test_failure_1(self):
            resource_conf = {
                "type": "Microsoft.StorageSync/storageSyncServices",
                "apiVersion": "2021-02-01",
                "name": "example-storage-sync",
                "properties": {
                    "storageSyncServiceStatus": "Registered",
                    "storageSyncServiceProperties": {
                        "trustState": "Enabled",
                        "storageSyncServiceUid": "65fdd65b-ea5d-4a00-bf7f-40c41ba39ae4",
                        "provisioningState": "Succeeded"
                    },
                    "location": "East US",
                    "incoming_traffic_policy": "AllowAllTraffic",
                    "tags": {
                        "foo": "bar"
                    }
                }
            }
            scan_result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(CheckResult.FAILED, scan_result)

            def test_success(self):
                resource_conf = {
                    "type": "Microsoft.StorageSync/storageSyncServices",
                    "apiVersion": "2021-02-01",
                    "name": "example-storage-sync",
                    "properties": {
                        "storageSyncServiceStatus": "Registered",
                        "storageSyncServiceProperties": {
                            "trustState": "Enabled",
                            "storageSyncServiceUid": "65fdd65b-ea5d-4a00-bf7f-40c41ba39ae4",
                            "provisioningState": "Succeeded"
                        },
                        "location": "East US",
                        "incoming_traffic_policy": "AllowVirtualNetworksOnly",
                        "tags": {
                            "foo": "bar"
                        }
                    }
                }
                scan_result = check.scan_resource_conf(conf=resource_conf)
                self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
