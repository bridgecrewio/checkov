import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.FrontdoorUseWAFMode import check


class TestFrontdoorUseWAFMode(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_frontdoor_firewall_policy" "example" {
              name                = "example-wafpolicy"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location

              custom_rules {
                name      = "Rule1"
                priority  = 1
                rule_type = "MatchRule"

                match_conditions {
                  match_variables {
                    variable_name = "RemoteAddr"
                  }

                  operator           = "IPMatch"
                  negation_condition = false
                  match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                }

                action = "Block"
              }

              custom_rules {
                name      = "Rule2"
                priority  = 2
                rule_type = "MatchRule"

                match_conditions {
                  match_variables {
                    variable_name = "RemoteAddr"
                  }

                  operator           = "IPMatch"
                  negation_condition = false
                  match_values       = ["192.168.1.0/24"]
                }

                match_conditions {
                  match_variables {
                    variable_name = "RequestHeaders"
                    selector      = "UserAgent"
                  }

                  operator           = "Contains"
                  negation_condition = false
                  match_values       = ["Windows"]
                }

                action = "Block"
              }

              policy_settings {
                enabled                     = false
                request_body_check          = true
                file_upload_limit_in_mb     = 100
                max_request_body_size_in_kb = 128
              }

              managed_rules {
                exclusion {
                  match_variable          = "RequestHeaderNames"
                  selector                = "x-company-secret-header"
                  selector_match_operator = "Equals"
                }
                exclusion {
                  match_variable          = "RequestCookieNames"
                  selector                = "too-tasty"
                  selector_match_operator = "EndsWith"
                }

                managed_rule_set {
                  type    = "OWASP"
                  version = "3.1"
                  rule_group_override {
                    rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                    disabled_rules = [
                      "920300",
                      "920440"
                    ]
                  }
                }
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_frontdoor_firewall_policy" "example" {
              name                = "example-wafpolicy"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location

              custom_rules {
                name      = "Rule1"
                priority  = 1
                rule_type = "MatchRule"

                match_conditions {
                  match_variables {
                    variable_name = "RemoteAddr"
                  }

                  operator           = "IPMatch"
                  negation_condition = false
                  match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                }

                action = "Block"
              }

              custom_rules {
                name      = "Rule2"
                priority  = 2
                rule_type = "MatchRule"

                match_conditions {
                  match_variables {
                    variable_name = "RemoteAddr"
                  }

                  operator           = "IPMatch"
                  negation_condition = false
                  match_values       = ["192.168.1.0/24"]
                }

                match_conditions {
                  match_variables {
                    variable_name = "RequestHeaders"
                    selector      = "UserAgent"
                  }

                  operator           = "Contains"
                  negation_condition = false
                  match_values       = ["Windows"]
                }

                action = "Block"
              }

              policy_settings {
                enabled                     = false
                mode                        = "Prevention"
                request_body_check          = true
                file_upload_limit_in_mb     = 100
                max_request_body_size_in_kb = 128
              }

              managed_rules {
                exclusion {
                  match_variable          = "RequestHeaderNames"
                  selector                = "x-company-secret-header"
                  selector_match_operator = "Equals"
                }
                exclusion {
                  match_variable          = "RequestCookieNames"
                  selector                = "too-tasty"
                  selector_match_operator = "EndsWith"
                }

                managed_rule_set {
                  type    = "OWASP"
                  version = "3.1"
                  rule_group_override {
                    rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                    disabled_rules = [
                      "920300",
                      "920440"
                    ]
                  }
                }
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success1(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_frontdoor_firewall_policy" "example" {
                      name                = "example-wafpolicy"
                      resource_group_name = azurerm_resource_group.example.name
                      location            = azurerm_resource_group.example.location

                      custom_rules {
                        name      = "Rule1"
                        priority  = 1
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                        }

                        action = "Block"
                      }

                      custom_rules {
                        name      = "Rule2"
                        priority  = 2
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24"]
                        }

                        match_conditions {
                          match_variables {
                            variable_name = "RequestHeaders"
                            selector      = "UserAgent"
                          }

                          operator           = "Contains"
                          negation_condition = false
                          match_values       = ["Windows"]
                        }

                        action = "Block"
                      }

                      policy_settings {
                        enabled                     = true
                        mode                        = "Prevention"
                        request_body_check          = true
                        file_upload_limit_in_mb     = 100
                        max_request_body_size_in_kb = 128
                      }

                      managed_rules {
                        exclusion {
                          match_variable          = "RequestHeaderNames"
                          selector                = "x-company-secret-header"
                          selector_match_operator = "Equals"
                        }
                        exclusion {
                          match_variable          = "RequestCookieNames"
                          selector                = "too-tasty"
                          selector_match_operator = "EndsWith"
                        }

                        managed_rule_set {
                          type    = "OWASP"
                          version = "3.1"
                          rule_group_override {
                            rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                            disabled_rules = [
                              "920300",
                              "920440"
                            ]
                          }
                        }
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_frontdoor_firewall_policy" "example" {
                      name                = "example-wafpolicy"
                      resource_group_name = azurerm_resource_group.example.name
                      location            = azurerm_resource_group.example.location

                      custom_rules {
                        name      = "Rule1"
                        priority  = 1
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                        }

                        action = "Block"
                      }

                      custom_rules {
                        name      = "Rule2"
                        priority  = 2
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24"]
                        }

                        match_conditions {
                          match_variables {
                            variable_name = "RequestHeaders"
                            selector      = "UserAgent"
                          }

                          operator           = "Contains"
                          negation_condition = false
                          match_values       = ["Windows"]
                        }

                        action = "Block"
                      }

                      policy_settings {
                        mode                        = "Prevention"
                        request_body_check          = true
                        file_upload_limit_in_mb     = 100
                        max_request_body_size_in_kb = 128
                      }

                      managed_rules {
                        exclusion {
                          match_variable          = "RequestHeaderNames"
                          selector                = "x-company-secret-header"
                          selector_match_operator = "Equals"
                        }
                        exclusion {
                          match_variable          = "RequestCookieNames"
                          selector                = "too-tasty"
                          selector_match_operator = "EndsWith"
                        }

                        managed_rule_set {
                          type    = "OWASP"
                          version = "3.1"
                          rule_group_override {
                            rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                            disabled_rules = [
                              "920300",
                              "920440"
                            ]
                          }
                        }
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success3(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_frontdoor_firewall_policy" "example" {
                      name                = "example-wafpolicy"
                      resource_group_name = azurerm_resource_group.example.name
                      location            = azurerm_resource_group.example.location

                      custom_rules {
                        name      = "Rule1"
                        priority  = 1
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                        }

                        action = "Block"
                      }

                      custom_rules {
                        name      = "Rule2"
                        priority  = 2
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24"]
                        }

                        match_conditions {
                          match_variables {
                            variable_name = "RequestHeaders"
                            selector      = "UserAgent"
                          }

                          operator           = "Contains"
                          negation_condition = false
                          match_values       = ["Windows"]
                        }

                        action = "Block"
                      }

                      policy_settings {
                        enabled                     = true
                        request_body_check          = true
                        file_upload_limit_in_mb     = 100
                        max_request_body_size_in_kb = 128
                      }

                      managed_rules {
                        exclusion {
                          match_variable          = "RequestHeaderNames"
                          selector                = "x-company-secret-header"
                          selector_match_operator = "Equals"
                        }
                        exclusion {
                          match_variable          = "RequestCookieNames"
                          selector                = "too-tasty"
                          selector_match_operator = "EndsWith"
                        }

                        managed_rule_set {
                          type    = "OWASP"
                          version = "3.1"
                          rule_group_override {
                            rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                            disabled_rules = [
                              "920300",
                              "920440"
                            ]
                          }
                        }
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success4(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_frontdoor_firewall_policy" "example" {
                      name                = "example-wafpolicy"
                      resource_group_name = azurerm_resource_group.example.name
                      location            = azurerm_resource_group.example.location

                      custom_rules {
                        name      = "Rule1"
                        priority  = 1
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24", "10.0.0.0/24"]
                        }

                        action = "Block"
                      }

                      custom_rules {
                        name      = "Rule2"
                        priority  = 2
                        rule_type = "MatchRule"

                        match_conditions {
                          match_variables {
                            variable_name = "RemoteAddr"
                          }

                          operator           = "IPMatch"
                          negation_condition = false
                          match_values       = ["192.168.1.0/24"]
                        }

                        match_conditions {
                          match_variables {
                            variable_name = "RequestHeaders"
                            selector      = "UserAgent"
                          }

                          operator           = "Contains"
                          negation_condition = false
                          match_values       = ["Windows"]
                        }

                        action = "Block"
                      }

                      managed_rules {
                        exclusion {
                          match_variable          = "RequestHeaderNames"
                          selector                = "x-company-secret-header"
                          selector_match_operator = "Equals"
                        }
                        exclusion {
                          match_variable          = "RequestCookieNames"
                          selector                = "too-tasty"
                          selector_match_operator = "EndsWith"
                        }

                        managed_rule_set {
                          type    = "OWASP"
                          version = "3.1"
                          rule_group_override {
                            rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
                            disabled_rules = [
                              "920300",
                              "920440"
                            ]
                          }
                        }
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_frontdoor_firewall_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
