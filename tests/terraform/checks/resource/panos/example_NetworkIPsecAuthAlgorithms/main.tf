# The "authentications" attribute can be used in either the panos_ipsec_crypto_profile or the panos_panorama_ipsec_crypto_profile resource.
# Both resource types are covered by this check.

# Fails

# Fails for each insecure algorithm on their own

resource "panos_ipsec_crypto_profile" "fail1" {
    name = "fail1"
    authentications = ["none"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail2" {
    name = "fail2"
    authentications = ["md5"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail3" {
    name = "fail3"
    authentications = ["sha1"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail4" {
    name = "fail4"
    template = "template-name"
    authentications = ["none"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail5" {
    name = "fail5"
    template = "template-name"
    authentications = ["md5"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail6" {
    name = "fail6"
    template = "template-name"
    authentications = ["sha1"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

# Fails with one secure and one insecure

resource "panos_ipsec_crypto_profile" "fail7" {
    name = "fail7"
    authentications = ["sha512", "sha1"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_ipsec_crypto_profile" "fail8" {
    name = "fail8"
    authentications = ["sha1", "sha512"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail9" {
    name = "fail9"
    template = "template-name"
    authentications = ["sha512", "sha1"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "fail10" {
    name = "fail10"
    template = "template-name"
    authentications = ["sha1", "sha512"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}



# Passes with single algorithms

resource "panos_ipsec_crypto_profile" "pass1" {
    name = "pass1"
    authentications = ["sha512"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass2" {
    name = "pass2"
    template = "template-name"
    authentications = ["sha512"]
    encryptions = ["aes-256-gcm"]
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

resource "panos_ipsec_crypto_profile" "pass5" {
    name = "pass5"
    authentications = ["sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass6" {
    name = "pass6"
    template = "template-name"
    authentications = ["sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

# Passes with multiple algorithms

resource "panos_ipsec_crypto_profile" "pass7" {
    name = "pass7"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}

resource "panos_panorama_ipsec_crypto_profile" "pass8" {
    name = "pass8"
    template = "template-name"
    authentications = ["sha384", "sha256"]
    encryptions = ["aes-256-gcm"]
    dh_group = "group14"
    lifetime_type = "hours"
    lifetime_value = 4
    lifesize_type = "mb"
    lifesize_value = 1
}
