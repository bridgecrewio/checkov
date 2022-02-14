# The DSRI setting can be applied in either the panos_security_policy resource or the panos_security_rule_group resource.
# Both resource types are covered by this check.

# DSRI is set to true, disabling server-to-client inspection, which is a fail
resource "panos_security_policy" "fail1" {
    rule {
        name = "my-rule"
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
        name = "my-rule"
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

# DSRI is set to false, ensuring server-to-client inspection is enable, which is a pass
resource "panos_security_policy" "pass1" {
    rule {
        name = "my-rule"
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

# DSRI is set to false, ensuring server-to-client inspection is enable, which is a pass
resource "panos_security_rule_group" "pass2" {
    rule {
        name = "my-rule"
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

# Not explicitly setting the DSRI attribute when creating a rule leads to the default setting of false, which ensures server-to-client inspection is enable, which is a pass
resource "panos_security_policy" "pass3" {
    rule {
        name = "my-rule"
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

# Not explicitly setting the DSRI attribute when creating a rule leads to the default setting of false, which ensures server-to-client inspection is enable, which is a pass
resource "panos_security_rule_group" "pass4" {
    rule {
        name = "my-rule"
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