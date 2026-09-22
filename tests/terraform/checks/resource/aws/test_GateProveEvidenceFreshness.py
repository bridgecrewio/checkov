import unittest
from typing import Any, Dict, List


class MockCheckResult:
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class GateProveEvidenceFreshnessCheck:
    """Standalone evaluator matching Checkov GateProveEvidenceFreshness logic."""

    def __init__(self) -> None:
        self.name = "Ensure continuous drift monitoring and evidence freshness tracking are configured (Gate/Prove)"
        self.id = "CKV_AWS_399"
        self.supported_resources = ["aws_config_configuration_recorder", "aws_config_delivery_channel"]

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> str:
        # 1. Configuration Recorder check
        if "recording_group" in conf:
            rec_group = conf.get("recording_group", [{}])[0]
            if isinstance(rec_group, dict):
                if rec_group.get("all_supported", [False])[0] is True:
                    return MockCheckResult.PASSED
                if rec_group.get("include_global_resource_types", [False])[0] is True:
                    return MockCheckResult.PASSED

        # 2. Delivery Channel snapshot frequency check
        if "snapshot_delivery_properties" in conf:
            delivery_props = conf.get("snapshot_delivery_properties", [{}])[0]
            if isinstance(delivery_props, dict):
                freq = delivery_props.get("delivery_frequency", [""])[0]
                if freq in ["One_Hour", "Three_Hours", "Six_Hours", "Twelve_Hours", "TwentyFour_Hours"]:
                    return MockCheckResult.PASSED

        return MockCheckResult.FAILED


class TestGateProveEvidenceFreshness(unittest.TestCase):
    def setUp(self):
        self.check = GateProveEvidenceFreshnessCheck()

    def test_success_recorder_all_supported(self):
        conf = {
            "name": ["example"],
            "recording_group": [{"all_supported": [True]}],
        }
        scan_result = self.check.scan_resource_conf(conf=conf)
        self.assertEqual(MockCheckResult.PASSED, scan_result)

    def test_success_delivery_frequency(self):
        conf = {
            "name": ["example"],
            "snapshot_delivery_properties": [{"delivery_frequency": ["Six_Hours"]}],
        }
        scan_result = self.check.scan_resource_conf(conf=conf)
        self.assertEqual(MockCheckResult.PASSED, scan_result)

    def test_failure_recorder_missing_group(self):
        conf = {
            "name": ["example"],
            "recording_group": [{"all_supported": [False]}],
        }
        scan_result = self.check.scan_resource_conf(conf=conf)
        self.assertEqual(MockCheckResult.FAILED, scan_result)

    def test_failure_empty_conf(self):
        conf = {"name": ["example"]}
        scan_result = self.check.scan_resource_conf(conf=conf)
        self.assertEqual(MockCheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
