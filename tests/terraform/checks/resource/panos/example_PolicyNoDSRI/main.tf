# The DSRI setting can be applied in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.

# DSRI is set to true, disabling server-to-client inspection, which is a fail
resource "panos_security_policy" "fail1" {
    rule {
        name = "my-bad-rule-fail1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = true
    }
}

# DSRI is set to true, disabling server-to-client inspection, which is a fail
resource "panos_security_rule_group" "fail2" {
    rule {
        name = "my-bad-rule-fail2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = true
    }
}

# DSRI is set to true in the second rule, disabling server-to-client inspection, which is a fail
resource "panos_security_policy" "fail3" {
    rule {
        name = "my-bad-fail3-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
    rule {
        name = "my-bad-fail3-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = true
    }
}

# DSRI is set to true in the second rule, disabling server-to-client inspection, which is a fail
resource "panos_security_rule_group" "fail4" {
    rule {
        name = "my-bad-fail4-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
    rule {
        name = "my-bad-fail4-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = true
    }
}

# DSRI is set to false, ensuring server-to-client inspection is enabled, which is a pass
resource "panos_security_policy" "pass1" {
    rule {
        name = "my-good-rule-pass1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
}

# DSRI is set to false, ensuring server-to-client inspection is enabled, which is a pass
resource "panos_security_rule_group" "pass2" {
    rule {
        name = "my-good-rule-pass2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
}

# Not explicitly setting the DSRI attribute when creating a rule leads to the default setting of false, which ensures server-to-client inspection is enabled, which is a pass
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-good-rule-pass3"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# Not explicitly setting the DSRI attribute when creating a rule leads to the default setting of false, which ensures server-to-client inspection is enabled, which is a pass
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-good-rule-pass4"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
    }
}

# DSRI is set to false in both rules, ensuring server-to-client inspection is enabled, which is a pass
resource "panos_security_policy" "pass5" {
    rule {
        name = "my-good-pass5-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
    rule {
        name = "my-good-pass5-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
}

# DSRI is set to false in both rules, ensuring server-to-client inspection is enabled, which is a pass
resource "panos_security_rule_group" "pass6" {
    rule {
        name = "my-good-pass6-rule1"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
    rule {
        name = "my-good-pass6-rule2"
        source_zones = ["any"]
        source_addresses = ["any"]
        source_users = ["any"]
        hip_profiles = ["any"]
        destination_zones = ["any"]
        destination_addresses = ["any"]
        applications = ["any"]
        categories = ["any"]
        services = ["any"]
        action = "allow"
        disable_server_response_inspection = false
    }
}