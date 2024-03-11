import unittest

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.terraform.checks.resource.registry import resource_registry


class TestAnyCheck(BaseResourceNegativeValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        name = "Ensure it ain't broke"
        id = "test/TestAnyNegativeCheck"
        categories = []
        supported_resources = ["doesnt_matter"]
        guideline = "https://docs.prismacloud.io/policy-reference/test-policies/test-any-negative-check"
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            guideline=guideline
        )

    def get_inspected_key(self):
        return "foo"

    def get_forbidden_values(self):
        return [ANY_VALUE]


class TestStaticCheck(BaseResourceNegativeValueCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        name = "Ensure it ain't broke"
        id = "test/TestStaticNegativeCheck"
        categories = []
        supported_resources = ["doesnt_matter"]
        guideline = "https://docs.prismacloud.io/policy-reference/test-policies/test-static-negative-check"
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            guideline=guideline
        )

    def get_inspected_key(self):
        return "foo"
    
    def get_forbidden_values(self):
        return ["not-foo", "not-bar"]


class Test(unittest.TestCase):
    def test_string_match_any(self):
        result = self._check(TestAnyCheck(),
                             {"foo": "bar"})
        self.assertEqual(result, CheckResult.FAILED)

    def test_string_match_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "bar"})
        self.assertEqual(result, CheckResult.PASSED)

    def test_string_mismatch_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "not-bar"})
        self.assertEqual(result, CheckResult.FAILED)

    def test_string_contains_var_any(self):
        result = self._check(TestAnyCheck(),
                             {"foo": "something-${var.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_string_contains_var_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "something-${var.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_var_any(self):
        result = self._check(TestAnyCheck(),
                             {"foo": "${var.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_var_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "${var.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_local_any(self):
        result = self._check(TestAnyCheck(),
                             {"foo": "${local.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_local_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "${local.whatever}"})
        self.assertEqual(result, CheckResult.UNKNOWN)

    def test_resource_any(self):
        result = self._check(TestAnyCheck(),
                             {"foo": "${aws_s3_bucket.foo.bucket}"})
        self.assertEqual(result, CheckResult.FAILED)

    def test_resource_static(self):
        result = self._check(TestStaticCheck(),
                             {"foo": "${aws_s3_bucket.foo.bucket}"})
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
