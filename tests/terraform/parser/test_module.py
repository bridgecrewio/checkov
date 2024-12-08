import os
import unittest
import shutil

import hcl2

from checkov.terraform.modules.module_utils import validate_malformed_definitions, clean_bad_definitions, \
    clean_parser_types, serialize_definitions
from checkov.terraform.tf_parser import TFParser
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR


class ModuleTest(unittest.TestCase):

    def setUp(self) -> None:
        from checkov.terraform.module_loading.registry import ModuleLoaderRegistry

        # needs to be reset, because the cache belongs to the class not instance
        ModuleLoaderRegistry.module_content_cache = {}

        self.resources_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./resources"))
        self.external_module_path = ''

    def tearDown(self) -> None:
        if os.path.exists(self.external_module_path):
            shutil.rmtree(self.external_module_path)

    def test_module_double_slash_cleanup(self):
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'double_slash.tf')) as f:
            tf = hcl2.load(f)
        non_malformed_definitions = validate_malformed_definitions(tf)
        definitions = {
            '/mock/path/to.tf': clean_bad_definitions(non_malformed_definitions)
        }
        module, _ = TFParser().parse_hcl_module_from_tf_definitions(definitions, '', 'terraform')
        print(module)
        self.assertEqual(1, len(module.blocks))
        self.assertEqual('ingress.annotations.kubernetes\\.io/ingress\\.class', module.blocks[0].attributes['set.name'])

    def test_module_double_slash_cleanup_string(self):
        tf = hcl2.loads("""
resource "helm_release" "test" {
  name       = "influxdb"
  repository = "https://helm.influxdata.com"
  chart      = "influxdb"
  namespace  = "influxdb"
  set {
    name  = "ingress.annotations.kubernetes\\.io/ingress\\.class"
    value = var.influxdb_ingress_annotations_kubernetes_ingress_class
  }
}
        """)
        non_malformed_definitions = validate_malformed_definitions(tf)
        definitions = {
            '/mock/path/to.tf': clean_bad_definitions(non_malformed_definitions)
        }
        module, _ = TFParser().parse_hcl_module_from_tf_definitions(definitions, '', 'terraform')
        print(module)
        self.assertEqual(1, len(module.blocks))
        self.assertEqual('ingress.annotations.kubernetes\\.io/ingress\\.class', module.blocks[0].attributes['set.name'])

    def test_module_with_resource_type_attribute(self):
        tf = hcl2.loads("""
resource "azurerm_security_center_subscription_pricing" "example" {
  tier = "free"
  resource_type = "VirtualMachines"
  extension {
    name = "ContainerRegistriesVulnerabilityAssessments"
  }
}
        """)
        non_malformed_definitions = validate_malformed_definitions(tf)
        definitions = {
            '/mock/path/to.tf': clean_bad_definitions(non_malformed_definitions)
        }
        module, _ = TFParser().parse_hcl_module_from_tf_definitions(definitions, '', 'terraform')
        self.assertEqual(1, len(module.blocks))
        self.assertEqual(['VirtualMachines'], module.blocks[0].attributes['_resource_type'])

    def test_parse_hcl_module_serialize_definitions(self):
        parser = TFParser()
        directory = os.path.join(self.resources_dir, "parser_nested_modules")
        self.external_module_path = os.path.join(directory, DEFAULT_EXTERNAL_MODULES_DIR)
        tf_definitions = parser.parse_directory(directory=directory, out_evaluations_context={})
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions_encoded = serialize_definitions(tf_definitions)
        self.assertEqual(tf_definitions_encoded, tf_definitions)
