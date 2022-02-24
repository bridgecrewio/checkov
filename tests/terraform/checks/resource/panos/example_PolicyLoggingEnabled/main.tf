# Logging can be enabled in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.
# Using "log_end" enables logging at session end which is in Palo Alto Networks best practices

# Fails

# Logging is set to false, disabling logging, which is a fail
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
        services = ["application-default"]
        action = "allow"
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = false
    }
}

# Logging is set to false, disabling logging, which is a fail
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
        services = ["application-default"]
        action = "allow"
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = false
    }
}

# Logging is set to false in the second rule, disabling logging, which is a fail
resource "panos_security_policy" "fail3" {
    rule {
        name = "my-bad-rule1-fail3"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
    rule {
        name = "my-bad-rule2-fail3"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = false
    }
}

# Logging is set to false in the second rule, disabling logging, which is a fail
resource "panos_security_rule_group" "fail4" {
    rule {
        name = "my-bad-rule1-fail4"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
    rule {
        name = "my-bad-rule2-fail4"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = false
    }
}

# Passes

# Logging is set to true, enabling logging, which is a pass
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
        services = ["application-default"]
        action = "allow"
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
}

# Logging is set to true, enabling logging, which is a pass
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
        services = ["application-default"]
        action = "allow"
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
}

# Not explicitly setting the log_end attribute when creating a rule leads to the default setting of true, which ensures logging is enabled, which is a pass
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-good-rule-pass3"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
}

# Not explicitly setting the log_end attribute when creating a rule leads to the default setting of true, which ensures logging is enabled, which is a pass
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-good-rule-pass4"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
}

# log_end is set to true in both rules, ensuring logging is enabled, which is a pass
resource "panos_security_policy" "pass5" {
    rule {
        name = "my-good-rule1-pass5"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
    rule {
        name = "my-good-rule2-pass5"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
}

# log_end is set to true in both rules, ensuring logging is enabled, which is a pass
resource "panos_security_rule_group" "pass6" {
    rule {
        name = "my-good-rule1-pass6"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
    rule {
        name = "my-good-rule2-pass6"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
        log_end = true
    }
}

# Not explicitly setting the log_end attribute when creating a rule leads to the default setting of true, which ensures logging is enabled, which is a pass for both rules
resource "panos_security_policy" "pass7" {
    rule {
        name = "my-good-rule1-pass7"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
    rule {
        name = "my-good-rule2-pass7"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
}

# Not explicitly setting the log_end attribute when creating a rule leads to the default setting of true, which ensures logging is enabled, which is a pass for both rules
resource "panos_security_rule_group" "pass8" {
    rule {
        name = "my-good-rule1-pass8"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
    rule {
        name = "my-good-rule2-pass8"
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
        description = "This rule is for..."
        log_setting = "my-log-fwd-profile"
    }
}
