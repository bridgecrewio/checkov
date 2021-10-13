import os
import unittest

import hcl2

from checkov.terraform.parser import validate_malformed_definitions, clean_bad_definitions, Parser


class ModuleTest(unittest.TestCase):
    def test_module_double_slash_cleanup(self):
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'double_slash.tf')) as f:
            tf = hcl2.load(f)
        non_malformed_definitions = validate_malformed_definitions(tf)
        definitions = {
            '/mock/path/to.tf': clean_bad_definitions(non_malformed_definitions)
        }
        module, _ = Parser().parse_hcl_module_from_tf_definitions(definitions, '', 'terraform')
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
        module, _ = Parser().parse_hcl_module_from_tf_definitions(definitions, '', 'terraform')
        print(module)
        self.assertEqual(1, len(module.blocks))
        self.assertEqual('ingress.annotations.kubernetes\\.io/ingress\\.class', module.blocks[0].attributes['set.name'])
