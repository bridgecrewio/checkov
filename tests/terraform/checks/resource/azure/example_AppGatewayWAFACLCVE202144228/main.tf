# pass

resource "azurerm_web_application_firewall_policy" "owasp_3_1_default" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.1"

      rule_group_override = [{}]
    }
  }

  policy_settings {}
}

resource "azurerm_web_application_firewall_policy" "owasp_3_2_default" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }

  policy_settings {}
}

resource "azurerm_web_application_firewall_policy" "version_3_1_default" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      version = "3.2"
    }
  }

  policy_settings {}
}

resource "azurerm_web_application_firewall_policy" "owasp_3_1_disabled_different" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.1"

      rule_group_override {
        rule_group_name = "REQUEST-944-APPLICATION-ATTACK-JAVA"
        disabled_rules = [
          "944200",
          "944210"
        ]
      }
    }
  }

  policy_settings {}
}

resource "azurerm_web_application_firewall_policy" "empty_disabled_rules" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.1"

      rule_group_override {
        rule_group_name = "REQUEST-944-APPLICATION-ATTACK-JAVA"
      }
    }
  }

  policy_settings {}
}

# fail

resource "azurerm_web_application_firewall_policy" "owasp_3_0" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.0"
    }
  }

  policy_settings {}
}

resource "azurerm_web_application_firewall_policy" "owasp_3_1_disabled" {
  location            = "germanywestcentral"
  name                = "example"
  resource_group_name = "example"

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.1"

      rule_group_override {
        rule_group_name = "REQUEST-944-APPLICATION-ATTACK-JAVA"
        disabled_rules = [
          "944200",
          "944240"
        ]
      }
    }
  }

  policy_settings {}
}
