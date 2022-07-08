# The "services" attribute can be defined in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.

# Note: Not explicitly setting the services attribute when creating a rule is not valid, the services attribute is mandatory and will fail Terraform validation at plan stage, so this is not covered in test cases

# Note: Setting an services list item of "any" alongside other services is not valid, "any" must be used on it's own, and if used in a list alongside other services names and will fail Terraform validation at apply stage, so this is not covered in test cases

# Services is set to any, which is a fail as it is overly permissive
resource "panos_security_policy" "fail1" {
    rule {
        name = "my-bad-rule-fail1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Services is set to any, which is a fail as it is overly permissive
resource "panos_security_rule_group" "fail2" {
    rule {
        name = "my-bad-rule-fail2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Services is set to non-any in the first rule, but any in the second rule, which is a fail as it is overly permissive
resource "panos_security_policy" "fail3" {
    rule {
        name = "my-bad-fail3-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-bad-fail3-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Services is set to non-any in the first rule, but any in the second rule, which is a fail as it is overly permissive
resource "panos_security_rule_group" "fail4" {
    rule {
        name = "my-bad-fail4-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-bad-fail4-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Services is set to a non-any value, which is a pass
resource "panos_security_policy" "pass1" {
    rule {
        name = "my-good-rule-pass1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# Services is set to a non-any value, which is a pass
resource "panos_security_rule_group" "pass2" {
    rule {
        name = "my-good-rule-pass2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# Services is set to a non-any value in both rules, which is a pass
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-good-pass3-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-good-pass3-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# Services is set to a non-any value in both rules, which is a pass
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-good-pass4-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-good-pass4-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# Services is set to multiple non-any values, which is a pass
resource "panos_security_policy" "pass5" {
    rule {
        name = "my-good-rule-pass5"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}

# Services is set to multiple non-any values, which is a pass
resource "panos_security_rule_group" "pass6" {
    rule {
        name = "my-good-rule-pass6"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}
