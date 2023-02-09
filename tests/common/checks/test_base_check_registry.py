import unittest

from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class TestCheck(BaseCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self, *supported_entities, id="CKV_T_1"):
        name = "Example check"
        categories = []
        supported_entities = list(supported_entities)
        block_type = "module"
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type=block_type)

    def scan_entity_conf(self, conf, entity_type):
        pass


# noinspection DuplicatedCode
class TestRunnerRegistry(unittest.TestCase):

    def test_add_non_wildcard(self):
        registry = BaseCheckRegistry('')
        resource_1_check = TestCheck("resource_1")
        registry.register(resource_1_check)
        checks = registry.get_checks("resource_1")
        self.assertEqual(1, len(checks))
        self.assertEqual(resource_1_check, checks[0])

        self.assertIn("resource_1", registry.checks)
        self.assertNotIn("resource_1", registry.wildcard_checks)

    def test_add_wildcard(self):
        registry = BaseCheckRegistry('')
        resource_s_check = TestCheck("resource_*")
        registry.register(resource_s_check)
        checks = registry.get_checks("resource_*")
        self.assertEqual(1, len(checks))
        self.assertEqual(resource_s_check, checks[0])

        self.assertNotIn("resource_*", registry.checks)
        self.assertIn("resource_*", registry.wildcard_checks)

    def test__is_wildcard(self):
        self.assertFalse(BaseCheckRegistry._is_wildcard(""))
        self.assertFalse(BaseCheckRegistry._is_wildcard("resource"))
        self.assertFalse(BaseCheckRegistry._is_wildcard("module"))
        self.assertFalse(BaseCheckRegistry._is_wildcard("aws_s3_bucket"))
        self.assertTrue(BaseCheckRegistry._is_wildcard("aws_*"))
        self.assertTrue(BaseCheckRegistry._is_wildcard("*"))
        self.assertTrue(BaseCheckRegistry._is_wildcard("aws_[^0-9]"))

    def test_get_check_by_id(self):
        registry = BaseCheckRegistry('')
        resource_1_check = TestCheck("resource_1", id="CKV_T_1")
        resource_2_check = TestCheck("resource_2", id="CKV_T_2")
        resource_as_check = TestCheck("resource_a*", id="CKV_T_3")
        resource_bs_check = TestCheck("resource_b*", id="CKV_T_4")
        registry.register(resource_1_check)
        registry.register(resource_2_check)
        registry.register(resource_as_check)
        registry.register(resource_bs_check)

        self.assertEqual(resource_1_check, registry.get_check_by_id("CKV_T_1"))
        self.assertEqual(resource_2_check, registry.get_check_by_id("CKV_T_2"))
        self.assertEqual(resource_as_check, registry.get_check_by_id("CKV_T_3"))
        self.assertEqual(resource_bs_check, registry.get_check_by_id("CKV_T_4"))
        self.assertIsNone(registry.get_check_by_id("CKV_T_5"))

    def test_get_check_no_wildcard(self):
        registry = BaseCheckRegistry('')
        resource_1_check = TestCheck("resource_1", id="CKV_T_1")
        resource_2_check1 = TestCheck("resource_2", id="CKV_T_2")
        resource_2_check2 = TestCheck("resource_2", id="CKV_T_3")
        registry.register(resource_1_check)
        registry.register(resource_2_check1)
        registry.register(resource_2_check2)

        resource_1_checks = registry.get_checks("resource_1")
        self.assertEqual(1, len(resource_1_checks))
        self.assertEqual(resource_1_check, resource_1_checks[0])

        resource_2_checks = registry.get_checks("resource_2")
        self.assertEqual(2, len(resource_2_checks))
        self.assertIn(resource_2_check1, resource_2_checks)
        self.assertIn(resource_2_check2, resource_2_checks)

        self.assertEqual(0, len(registry.get_checks("resource")))
        self.assertEqual(0, len(registry.get_checks("resource_10")))

    def test_get_check_wildcard(self):
        registry = BaseCheckRegistry('')
        resource_s_check = TestCheck("resource_*", id="CKV_T_1")
        resource_as_check = TestCheck("resource_a*", id="CKV_T_2")
        s_check = TestCheck("*", id="CKV_T_3")
        s_2_check = TestCheck("*_2", id="CKV_T_4")
        registry.register(resource_s_check)
        registry.register(resource_as_check)
        registry.register(s_check)
        registry.register(s_2_check)

        resource_1_checks = registry.get_checks("resource_1")
        self.assertEqual(2, len(resource_1_checks))
        self.assertIn(s_check, resource_1_checks)
        self.assertIn(resource_s_check, resource_1_checks)

        resource_2_checks = registry.get_checks("resource_2")
        self.assertEqual(3, len(resource_2_checks))
        self.assertIn(s_check, resource_2_checks)
        self.assertIn(s_2_check, resource_2_checks)
        self.assertIn(resource_s_check, resource_2_checks)

        resource__checks = registry.get_checks("resource_")
        self.assertEqual(2, len(resource__checks))
        self.assertIn(s_check, resource__checks)
        self.assertIn(resource_s_check, resource__checks)

        resource_abc_checks = registry.get_checks("resource_abc")
        self.assertEqual(3, len(resource_abc_checks))
        self.assertIn(s_check, resource_abc_checks)
        self.assertIn(resource_s_check, resource_abc_checks)
        self.assertIn(resource_as_check, resource_abc_checks)

        r_checks = registry.get_checks("r")
        self.assertEqual(1, len(r_checks))
        self.assertIn(s_check, r_checks)

        resource_checks = registry.get_checks("resource")
        self.assertEqual(1, len(resource_checks))
        self.assertIn(s_check, resource_checks)

        resource_checks = registry.get_checks("resource_ABC")
        self.assertEqual(2, len(resource_checks))
        self.assertIn(s_check, resource_checks)
        self.assertIn(resource_s_check, resource_checks)

    def test_get_check_mixed(self):
        registry = BaseCheckRegistry('')
        resource_1_check = TestCheck("resource_1", id="CKV_T_1")
        resource_2_check = TestCheck("resource_2", id="CKV_T_2")
        resource_s_check = TestCheck("resource_*", id="CKV_T_4")
        resource_as_check = TestCheck("resource_a*", id="CKV_T_3")
        s_check = TestCheck("*", id="CKV_T_4")
        s_2_check = TestCheck("*_2", id="CKV_T_5")
        registry.register(resource_1_check)
        registry.register(resource_2_check)
        registry.register(resource_s_check)
        registry.register(resource_as_check)
        registry.register(s_check)
        registry.register(s_2_check)

        resource_1_checks = registry.get_checks("resource_1")
        self.assertEqual(3, len(resource_1_checks))
        self.assertIn(s_check, resource_1_checks)
        self.assertIn(resource_1_check, resource_1_checks)
        self.assertIn(resource_s_check, resource_1_checks)

        resource_10_checks = registry.get_checks("resource_10")
        self.assertEqual(2, len(resource_10_checks))
        self.assertIn(s_check, resource_10_checks)
        self.assertIn(resource_s_check, resource_10_checks)

        resource_2_checks = registry.get_checks("resource_2")
        self.assertEqual(4, len(resource_2_checks))
        self.assertIn(s_check, resource_2_checks)
        self.assertIn(s_2_check, resource_2_checks)
        self.assertIn(resource_2_check, resource_2_checks)
        self.assertIn(resource_s_check, resource_2_checks)

        resource__checks = registry.get_checks("resource_")
        self.assertEqual(2, len(resource__checks))
        self.assertIn(s_check, resource__checks)
        self.assertIn(resource_s_check, resource__checks)


if __name__ == '__main__':
    unittest.main()
