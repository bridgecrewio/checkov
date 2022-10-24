# Setting the http attribute to true turns on HTTP for management, and is therefore a fail, we only want to see HTTPS in use
resource "panos_management_profile" "fail" {
    name = "my-mgmt-profile"
    http = true
}

# Setting the http attribute to false leaves HTTP disabled for management, and is therefore a pass
resource "panos_management_profile" "pass1" {
    name = "my-mgmt-profile"
    http = false
}

# Not explicitly setting the http attribute when creating a mgmt profile leads to the default setting of false, which leaves HTTP disabled for management, and is therefore a pass
resource "panos_management_profile" "pass2" {
    name = "my-mgmt-profile"
}