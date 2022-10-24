# The "encryptions" attribute can be used in either the panos_ipsec_crypto_profile or the panos_panorama_ipsec_crypto_profile resource.
# Both resource types are covered by this check.

# Fails

# Fails for each insecure algorithm on their own
resource "panos_ipsec_crypto_profile" "fail1" {
    name = "fail1"
    authentications = ["sha384"]
    encryptions = ["des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail2" {
    name = "fail2"
    authentications = ["sha384"]
    encryptions = ["3des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail3" {
    name = "fail3"
    authentications = ["sha384"]
    encryptions = ["aes-128-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail4" {
    name = "fail4"
    authentications = ["sha384"]
    encryptions = ["aes-192-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail5" {
    name = "fail5"
    authentications = ["sha384"]
    encryptions = ["aes-256-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail6" {
    name = "fail6"
    authentications = ["sha384"]
    encryptions = ["null"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail7" {
    name = "fail7"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail8" {
    name = "fail8"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["3des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail9" {
    name = "fail9"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-128-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail10" {
    name = "fail10"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-192-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail11" {
    name = "fail11"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-256-cbc"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail12" {
    name = "fail12"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["null"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

# Fails with one secure and one insecure

resource "panos_ipsec_crypto_profile" "fail13" {
    name = "fail13"
    authentications = ["sha384"]
    encryptions = ["3des", "aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail14" {
    name = "fail14"
    authentications = ["sha384"]
    encryptions = ["aes-256-gcm", "3des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail15" {
    name = "fail15"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["3des", "aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail16" {
    name = "fail16"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-256-gcm", "3des"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}



# Passes with single algorithms

resource "panos_ipsec_crypto_profile" "pass1" {
    name = "pass1"
    authentications = ["sha384"]
    encryptions = ["aes-128-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass2" {
    name = "pass2"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-128-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "pass3" {
    name = "pass3"
    authentications = ["sha384"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass4" {
    name = "pass4"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

# Passes with multiple algorithms

resource "panos_ipsec_crypto_profile" "pass5" {
    name = "pass5"
    authentications = ["sha384"]
    encryptions = ["aes-128-gcm", "aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass6" {
    name = "pass6"
    template = "template-name"
    authentications = ["sha384"]
    encryptions = ["aes-128-gcm", "aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}
