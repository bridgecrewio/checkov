# The description be used in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.

# Fails

# Security rules should should have a description populated to communicate the purpose for the rule, absence of the description attribute is therefore a fail
resource "panos_security_policy" "fail1" {
    rule {
        name = "my-bad-rule-fail1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, absence of the description attribute is therefore a fail
resource "panos_security_rule_group" "fail2" {
    rule {
        name = "my-bad-rule-fail2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, any empty description attribute is therefore a fail
resource "panos_security_policy" "fail3" {
    rule {
        name = "my-bad-rule-fail3"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = ""
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, an empty description attribute is therefore a fail
resource "panos_security_rule_group" "fail4" {
    rule {
        name = "my-bad-rule-fail4"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = ""
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, any empty description attribute is therefore a fail (2nd rule)
resource "panos_security_policy" "fail5" {
    rule {
        name = "my-good-rule-fail5"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-bad-rule-fail5"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = ""
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, an empty description attribute is therefore a fail (2nd rule)
resource "panos_security_rule_group" "fail6" {
    rule {
        name = "my-good-rule-fail6"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-bad-rule-fail6"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = ""
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, absence of the description attribute is therefore a fail (2nd rule)
resource "panos_security_policy" "fail7" {
    rule {
        name = "my-good-rule-fail7"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-bad-rule-fail7"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, absence of the description attribute is therefore a fail (2nd rule)
resource "panos_security_rule_group" "fail8" {
    rule {
        name = "my-good-rule-fail8"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-bad-rule-fail8"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, any empty description attribute is therefore a fail (even strings of spaces) 
resource "panos_security_policy" "fail9" {
    rule {
        name = "my-bad-rule-fail9"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "  "
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, an empty description attribute is therefore a fail (even strings of spaces)
resource "panos_security_rule_group" "fail10" {
    rule {
        name = "my-bad-rule-fail10"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "  "
    }
}


# Passes

# Security rules should should have a description populated to communicate the purpose for the rule
resource "panos_security_policy" "pass1" {
    rule {
        name = "my-good-rule-pass1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule
resource "panos_security_rule_group" "pass2" {
    rule {
        name = "my-good-rule-pass2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, test block with 2 passing rules 
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-good-rule-pass3-1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-good-rule-pass3-2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
}

# Security rules should should have a description populated to communicate the purpose for the rule, test block with 2 passing rules
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-good-rule-pass4-1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
    rule {
        name = "my-good-rule-pass4-2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        description = "This rule is for..."
    }
}