import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.terraform.checks.resource.registry import resource_registry

class TestDynamicCheck(BaseResourceValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        super().__init__("Ensure it ain't broke", "test/TestDynamicCheck", [], ["doesnt_matter"])

    def get_inspected_key(self):
        return "dynamic_block_name/[0]/foo"

    def get_expected_value(self):
        return "bar"

class TestNestedDynamicCheck(BaseResourceValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        super().__init__("Ensure it ain't broke", "test/TestNestedDynamicCheck", [], ["doesnt_matter"])

    def get_inspected_key(self):
        return "outside/dynamic_block_name/[0]/foo"

    def get_expected_value(self):
        return "bar"


class TestNestedMultipleDynamicCheckBlock1(BaseResourceValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        super().__init__("Ensure it ain't broke", "test/TestNestedMultipleDynamicCheckBlock1", [], ["doesnt_matter"])

    def get_inspected_key(self):
        return "outside/dynamic_block_name/[0]/dynamic_block_1/[0]/key"

    def get_expected_value(self):
        return 1

class TestNestedMultipleDynamicCheckBlock2(BaseResourceValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        super().__init__("Ensure it ain't broke", "test/TestNestedMultipleDynamicCheckBlock2", [], ["doesnt_matter"])

    def get_inspected_key(self):
        return "outside/dynamic_block_name/[0]/dynamic_block_2/[0]/key"

    def get_expected_value(self):
        return "2"

class Test(unittest.TestCase):
    def test_dynamic(self):
        data = {
            "dynamic": [{
                "dynamic_block_name": {
                    "content": {
                        "foo": "bar"
                    }
                }
            }]
        }

        result = self._check(TestDynamicCheck(),data)
        self.assertEqual(result, CheckResult.PASSED)

    def test_dynamic_nested(self):
        data = {
            "outside": {
                "dynamic": [{
                    "dynamic_block_name": {
                        "content": {
                            "foo": "bar"
                        }
                    }
                }]
            }
        }

        result = self._check(TestNestedDynamicCheck(), data)
        self.assertEqual(result, CheckResult.PASSED)

    def multipleDynamicBlockData(self):
        return {
            "outside": {
                "dynamic": [{
                    "dynamic_block_name": {
                        "content": {
                            "dynamic": [{
                                "dynamic_block_1": {
                                    "content": {
                                        "key": 1
                                    }
                                },
                                "dynamic_block_2": {
                                    "content": {
                                        "key": "2"
                                    }
                                }
                            }]
                        }
                    }
                }]
            }
        }

    def test_nested_multiple_dynamic_block_1(self):
        result = self._check(TestNestedMultipleDynamicCheckBlock1(), self.multipleDynamicBlockData())
        self.assertEqual(result, CheckResult.PASSED)

    def test_nested_multiple_dynamic_block_2(self):
        result = self._check(TestNestedMultipleDynamicCheckBlock2(), self.multipleDynamicBlockData())
        self.assertEqual(result, CheckResult.PASSED)


    @staticmethod
    def _check(check, data):
        return check.scan_resource_conf(data)

    # This will install a custom check, so setUp/tearDown will ensure the check list is unchanged
    # globally by our changes.
    def setUp(self) -> None:
        self.check_list_before = resource_registry.checks.copy()  # copy
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()
        resource_registry.checks = self.check_list_before
        self.check_list_before = None


