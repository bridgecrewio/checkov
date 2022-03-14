# The "protocol" attribute can be used in either the panos_ipsec_crypto_profile or the panos_panorama_ipsec_crypto_profile resource.
# Both resource types are covered by this check.

# Fails

# Setting the protocol attribute to "ah" uses Authentication Header, which only provides connection authentication and not confidentiality, and is therefore a fail, we only want to see ESP in use
resource "panos_ipsec_crypto_profile" "fail1" {
    name = "fail1"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
    protocol = "ah"
}
# Setting the protocol attribute to "ah" uses Authentication Header, which only provides connection authentication and not confidentiality, and is therefore a fail, we only want to see ESP in use
resource "panos_panorama_ipsec_crypto_profile" "fail2" {
    name = "fail2"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
    protocol = "ah"
}

# Passes

# Setting the protocol attribute to "esp" uses Encapsulating Security Payload, which provides connection authentication and confidentiality, and is therefore a pass
resource "panos_ipsec_crypto_profile" "pass1" {
    name = "pass1"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
    protocol = "esp"
}
# Setting the protocol attribute to "esp" uses Encapsulating Security Payload, which provides connection authentication and confidentiality, and is therefore a pass
resource "panos_panorama_ipsec_crypto_profile" "pass2" {
    name = "pass2"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
    protocol = "esp"
}

# Not explicitly setting the protocol attribute when creating an IPsec profile leads to the default setting of "esp", using Encapsulating Security Payload, which provides connection authentication and confidentiality, and is therefore a pass
resource "panos_ipsec_crypto_profile" "pass3" {
    name = "pass3"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}
# Not explicitly setting the protocol attribute when creating an IPsec profile leads to the default setting of "esp", using Encapsulating Security Payload, which provides connection authentication and confidentiality, and is therefore a pass
resource "panos_panorama_ipsec_crypto_profile" "pass4" {
    name = "pass4"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}
