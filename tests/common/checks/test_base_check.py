import unittest

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
    def scan_entity_conf(self, conf):
        """
        My documentation
        :param conf:
        :return:
        """
        return CheckResult.PASSED


class TestCheckDetails(BaseCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        name = "Another Example check"
        categories = []
        id = "CKV_T_2"
        supported_entities = ["my_resource_type"]
        block_type = "resource"
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type=block_type)

    # noinspection PyMethodOverriding
    def scan_entity_conf(self, conf):
        """
        My documentation
        :param conf:
        :return:
        """
        if conf.get("value")[0]:
            self.details.append("This check PASSED...")
            return CheckResult.PASSED
        else:
            self.details.append("This check FAILED...")
            return CheckResult.FAILED


# noinspection DuplicatedCode
class TestBaseCheck(unittest.TestCase):

    def test_entity_type_is_not_required_in_signature(self):
        registry = BaseCheckRegistry(report_type='')
        check = TestCheckTypeNotInSignature()
        registry.register(check)

        # noinspection PyArgumentList
        scan_result = check.scan_entity_conf({}, "Some name")
        self.assertEqual(CheckResult.PASSED, scan_result)
        self.assertEqual(check.scan_entity_conf.__doc__, """
        My documentation
        :param conf:
        :return:
        """)

    def test_invalid_signature_is_detected(self):
        with self.assertRaises(NotImplementedError) as context:
            class TestCheckUnknownSignature(BaseCheck):

                def __init__(self):
                    name = "Example check"
                    categories = []
                    id = "CKV_T_1"
                    supported_entities = ["module"]
                    block_type = "module"
                    super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                                     block_type=block_type)

                # noinspection PyMethodOverriding
                def scan_entity_conf(self, conf, some_unexpected_parameter_123):
                    return CheckResult.PASSED
        self.assertIsInstance(context.exception, NotImplementedError)
        self.assertEqual(
            "The signature ((\'self\', \'conf\', \'some_unexpected_parameter_123\'), None, None) for scan_entity_conf "
            "is not supported.",
            context.exception.args[0]
        )

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


if __name__ == '__main__':
    unittest.main()
