import os
import unittest

from unittest import mock
from parameterized import parameterized

from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult


class TestCheckTypeNotInSignature(BaseCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        name = "Example check"
        categories = []
        id = "CKV_T_1"
        supported_entities = ["module"]
        block_type = "module"
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type=block_type)

    # noinspection PyMethodOverriding
    def scan_entity_conf(self, conf, entity_type):
        """
        My documentation
        :param conf:
        :return:
        """
        return CheckResult.PASSED


class TestCheckDetails(BaseCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self, fail_check=False):
        name = "Another Example check"
        categories = []
        id = "CKV_T_2"
        supported_entities = ["my_resource_type"]
        block_type = "resource"
        self.fail_check = fail_check
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type=block_type)

    # noinspection PyMethodOverriding
    def scan_entity_conf(self, conf, entity_type):
        """
        My documentation
        :param conf:
        :return:
        """
        if self.fail_check:
            raise Exception("An error")
        if conf.get("value")[0]:
            self.details.append("This check PASSED...")
            return CheckResult.PASSED
        else:
            self.details.append("This check FAILED...")
            return CheckResult.FAILED


def _clean_doc(st: str) -> list[str]:
    return [line.strip() for line in st.splitlines() if not line.isspace()]


# noinspection DuplicatedCode
class TestBaseCheck(unittest.TestCase):

    def test_entity_type_is_not_required_in_signature(self):
        registry = BaseCheckRegistry(report_type='')
        check = TestCheckTypeNotInSignature()
        registry.register(check)

        # noinspection PyArgumentList
        scan_result = check.scan_entity_conf({}, "Some name")
        self.assertEqual(CheckResult.PASSED, scan_result)
        self.assertEqual(_clean_doc(check.scan_entity_conf.__doc__), _clean_doc("""
        My documentation
        :param conf:
        :return:
        """))

    def test_invalid_signature_is_detected(self):
        with self.assertRaises(TypeError) as context:
            class TestCheckUnknownSignature(BaseCheck):

                def __init__(self):
                    name = "Example check"
                    categories = []
                    id = "CKV_T_1"
                    supported_entities = ["module"]
                    block_type = "module"
                    super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                                     block_type=block_type)

            TestCheckUnknownSignature()

        self.assertIsInstance(context.exception, TypeError)
        self.assertRegex(context.exception.args[0], r"Can't instantiate abstract class TestCheckUnknownSignature")

    def test_details_reinitializing_after_execution(self):
        check = TestCheckDetails()
        self.assertEqual(0, len(check.details))
        result = check.run("test.tf", {"value": ["True"]}, "my_resource", "resource", {})
        self.assertEqual(CheckResult.PASSED, result["result"])
        self.assertEqual(1, len(check.details))
        self.assertIn("This check PASSED...", check.details)
        result = check.run("test.tf", {"value": [""]}, "my_resource_2", "resource", {})
        self.assertEqual(CheckResult.FAILED, result["result"])
        self.assertEqual(1, len(check.details))
        self.assertIn("This check FAILED...", check.details)

    @parameterized.expand([
        ("WARNING",),
        ("ERROR",)
    ])
    def test_check_fail_log_level_error(self, log_level):
        with self.assertLogs(level=log_level) as log, mock.patch.dict(os.environ,
                                                                      {'CHECKOV_CHECK_FAIL_LEVEL': log_level}, clear=True):
            check = TestCheckDetails(fail_check=True)
            self.assertEqual(0, len(check.details))
            try:
                check.run("test.tf", {"value": ["True"]}, "my_resource", "resource", {})
            except Exception:
                self.assertEqual(len(log.output), 1)


if __name__ == '__main__':
    unittest.main()
