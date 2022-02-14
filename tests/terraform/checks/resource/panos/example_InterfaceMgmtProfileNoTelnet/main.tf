# Setting the telnet attribute to true turns on Telnet for management, and is therefore a fail, we only want to see SSH in use
resource "panos_management_profile" "fail" {
    name = "my-mgmt-profile"
    telnet = true
}

# Setting the telnet attribute to false leaves Telnet disabled for management, and is therefore a pass
resource "panos_management_profile" "pass1" {
    name = "my-mgmt-profile"
    telnet = false
}

# Not explicitly setting the telnet attribute when creating a mgmt profile leads to the default setting of false, which leaves Telnet disabled for management, and is therefore a pass
resource "panos_management_profile" "pass2" {
    telnet = "my-mgmt-profile"
}