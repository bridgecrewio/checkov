import unittest

import json

from checkov.arm.checks.resource.AzureDefenferOnStorage import check
from checkov.common.models.enums import CheckResult


class TestAzureDefenderOnStorage(unittest.TestCase):
    def test_failure1(self):
        resource_conf = {
            "type": "Microsoft.Security/pricings",
            "apiVersion": "2018-06-01",
            "name": "azurermSecurityCenterSubscriptionPricing",
            "properties": {
                "tier": "Free",
                "resourceType": "StorageAccounts"
            }
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "type": "Microsoft.Security/pricings",
            "apiVersion": "2018-06-01",
            "name": "azurermSecurityCenterSubscriptionPricing",
            "properties": {
                "tier": "Standard",
                "resourceType": "StorageAccounts"
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()