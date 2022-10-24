# The "source_addresses" and "destination_addresses" attributes can be defined in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.

# Note: Not explicitly setting the "source_addresses" and "destination_addresses" attributes when creating a rule is not valid, the "source_addresses" and "destination_addresses" attributes are mandatory and will fail Terraform validation at plan stage, so this is not covered in test cases

# Note: Setting a "source_addresses" or "destination_addresses" list item of "any" alongside other items is not technically valid PAN-OS configuration, but the provider and the OS accept it (even though it can't be configured this way in the GUI). However, because it is possible to create this type of configuration in Terraform without error, there are test cases for it


# Passes

# "source_addresses" is set to a non-any value, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_policy" "pass1" {
    rule {
        name = "my-good-rule-pass1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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

# "source_addresses" is set to a non-any value, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_rule_group" "pass2" {
    rule {
        name = "my-good-rule-pass2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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

# "destination_addresses" is set to a non-any value, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-good-rule-pass3"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "destination_addresses" is set to a non-any value, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-good-rule-pass4"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "destination_addresses" is set to a non-any value in both rules, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_policy" "pass5" {
    rule {
        name = "my-good-pass5-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-good-pass5-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.4.4/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "destination_addresses" is set to a non-any value in both rules, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_rule_group" "pass6" {
    rule {
        name = "my-good-pass6-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
    rule {
        name = "my-good-pass5-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.4.4/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" is set to a non-any value in both rules, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_policy" "pass7" {
    rule {
        name = "my-good-pass7-rule1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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
        name = "my-good-pass7-rule2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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

# "source_addresses" is set to a non-any value in both rules, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_rule_group" "pass8" {
    rule {
        name = "my-good-pass8-rule1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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
        name = "my-good-pass8-rule2"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
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

# "destination_addresses" is set to multiple non-any values, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_policy" "pass9" {
    rule {
        name = "my-good-rule-pass9"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32", "8.8.4.4/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "destination_addresses" is set to multiple non-any values, which is a pass ("source_addresses" set to any is valid for hosting Internet-facing workloads)
resource "panos_security_rule_group" "pass10" {
    rule {
        name = "my-good-rule-pass10"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32", "8.8.4.4/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" is set to multiple non-any values, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_policy" "pass11" {
    rule {
        name = "my-good-rule-pass11"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32","10.10.10.11/32"]
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

# "source_addresses" is set to multiple non-any values, which is a pass ("destination_addresses" set to any is valid for traffic destined for the Internet)
resource "panos_security_rule_group" "pass12" {
    rule {
        name = "my-good-rule-pass12"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32","10.10.10.11/32"]
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

# "source_addresses" and "destination_addresses" are set to non-any values, which is a pass
resource "panos_security_policy" "pass13" {
    rule {
        name = "my-good-rule-pass13"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are set to non-any values, which is a pass
resource "panos_security_rule_group" "pass14" {
    rule {
        name = "my-good-rule-pass14"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["application-default"]
        action = "allow"
    }
}




# Fails

# "source_addresses" and "destination_addresses" are both set to any, which is a fail as it is overly permissive
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
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any, which is a fail as it is overly permissive
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
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any in the second rule, which is a fail as it is overly permissive
resource "panos_security_policy" "fail3" {
    rule {
        name = "my-bad-fail3-rule1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
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
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any in the second rule, which is a fail as it is overly permissive
resource "panos_security_rule_group" "fail4" {
    rule {
        name = "my-bad-fail4-rule1"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["8.8.8.8/32"]
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
        services = ["application-default"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any, even though the source_address has other list items after any, which is a fail as it is overly permissive 
resource "panos_security_policy" "fail5" {
    rule {
        name = "my-bad-rule-fail5"
        source_zones = ["any"]
        source_addresses = ["any","10.10.10.10/32"]
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

# "source_addresses" and "destination_addresses" are both set to any, even though the source_address has other list items before any, which is a fail as it is overly permissive 
resource "panos_security_rule_group" "fail6" {
    rule {
        name = "my-bad-rule-fail6"
        source_zones = ["any"]
        source_addresses = ["10.10.10.10/32","any"]
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

# "source_addresses" and "destination_addresses" are both set to any, even though the destination_addresses has other list items after any, which is a fail as it is overly permissive 
resource "panos_security_policy" "fail7" {
    rule {
        name = "my-bad-rule-fail7"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any","10.10.10.10/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any, even though the destination_address has other list items before any, which is a fail as it is overly permissive 
resource "panos_security_rule_group" "fail8" {
    rule {
        name = "my-bad-rule-fail8"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["10.10.10.10/32","any"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any, even though both source_address and destination_address have other list items after any, which is a fail as it is overly permissive 
resource "panos_security_policy" "fail9" {
    rule {
        name = "my-bad-rule-fail9"
        source_zones = ["any"]
        source_addresses = ["any","10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any","10.10.10.10/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}

# "source_addresses" and "destination_addresses" are both set to any, even though both source_address and destination_address have other list items after any, which is a fail as it is overly permissive 
resource "panos_security_rule_group" "fail10" {
    rule {
        name = "my-bad-rule-fail10"
        source_zones = ["any"]
        source_addresses = ["any","10.10.10.10/32"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any","10.10.10.10/32"]
        applications = ["web-browsing","ssl"]
        categories = ["any"]
        services = ["service-http","service-https"]
        action = "allow"
    }
}
