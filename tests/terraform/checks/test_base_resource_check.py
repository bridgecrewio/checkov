import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.resource.registry import resource_registry as registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestWildcardEntities(unittest.TestCase):

    def test_contains_unrendered_variable(self):
        self.assertTrue(BaseResourceCheck.contains_unrendered_value('var.xyz'))
        self.assertTrue(BaseResourceCheck.contains_unrendered_value('local.xyz'))
        self.assertTrue(BaseResourceCheck.contains_unrendered_value('${var.xyz}'))
        self.assertTrue(BaseResourceCheck.contains_unrendered_value('${local.xyz}'))

        self.assertFalse(BaseResourceCheck.contains_unrendered_value('xyz'))
        self.assertFalse(BaseResourceCheck.contains_unrendered_value('123'))
        self.assertFalse(BaseResourceCheck.contains_unrendered_value(123))
        self.assertFalse(BaseResourceCheck.contains_unrendered_value(True))


if __name__ == '__main__':
    unittest.main()
