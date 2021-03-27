import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.VMCredsInCustomData import check

resources = """
resource "azurerm_virtual_machine" "secret" {
  name                  = "${var.prefix}-vm"

  os_profile {
    computer_name  = "hostname"
    custom_data = <<EOF
0000-0000-0000-0000-000000000000
EOF
  }
}

resource "azurerm_virtual_machine" "no_secret" {
  name                  = "${var.prefix}-vm"

  os_profile {
    computer_name  = "hostname"
    custom_data = <<EOF
hello
EOF
  }
}

resource "azurerm_virtual_machine" "no_custom_data" {
  name                  = "${var.prefix}-vm"

  os_profile {
    computer_name  = "hostname"
  }
}

resource "azurerm_virtual_machine" "no_os_profile" {
  name                  = "${var.prefix}-vm"
}
"""


class TestVMCredsInCustomData(unittest.TestCase):
    def test(self):
        hcl_res = hcl2.loads(resources)

        resource_conf = hcl_res["resource"][0]["azurerm_virtual_machine"]["secret"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

        resource_conf = hcl_res["resource"][1]["azurerm_virtual_machine"]["no_secret"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

        resource_conf = hcl_res["resource"][2]["azurerm_virtual_machine"][
            "no_custom_data"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

        resource_conf = hcl_res["resource"][3]["azurerm_virtual_machine"][
            "no_os_profile"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
