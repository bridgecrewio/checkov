import unittest

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class TestWildcardEntities(unittest.TestCase):
    def test_contains_unrendered_variable(self):
        self.assertTrue(BaseResourceCheck._is_variable_dependant("var.xyz"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("local.xyz"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("module.xyz"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("${var.xyz}"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("${local.xyz}"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("${module.xyz}"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("aws_ssm_parameter.secret.value"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("azuread_service_principal_password.gh_actions.value"))
        self.assertTrue(BaseResourceCheck._is_variable_dependant("lookup(var.https_listeners,\"protocol\",\"HTTPS\")"))
        self.assertFalse(BaseResourceCheck._is_variable_dependant("xyz"))
        self.assertFalse(BaseResourceCheck._is_variable_dependant("123"))
        self.assertFalse(BaseResourceCheck._is_variable_dependant(123))
        self.assertFalse(BaseResourceCheck._is_variable_dependant(True))


if __name__ == "__main__":
    unittest.main()
