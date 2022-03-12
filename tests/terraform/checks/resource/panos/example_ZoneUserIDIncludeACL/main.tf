# If User-ID is enabled for a zone (optional), an "include ACL" should be defined to provide scope for User-ID. This can be configured in "panos_zone" or "panos_panorama_zone" resources. Both resource types are covered by this check.

# Passes

# User-ID enabled, Include ACL defined, single entry in list
resource "panos_zone" "pass1" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["10.0.0.0./8"]
}
resource "panos_panorama_zone" "pass2" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["10.0.0.0./8"]
}

# User-ID enabled, Include ACL defined, double entry in list
resource "panos_zone" "pass3" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["10.0.0.0./8", "192.168.0.0/16"]
}
resource "panos_panorama_zone" "pass4" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["10.0.0.0./8", "192.168.0.0/16"]
}

# User-ID not enabled, Include ACL not required
resource "panos_zone" "pass5" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
}
resource "panos_panorama_zone" "pass6" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
}

# Fails

# User-ID enabled, Include ACL undefined
resource "panos_zone" "fail1" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
}
resource "panos_panorama_zone" "fail2" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
}

# User-ID enabled, Include ACL defined, empty string in list
resource "panos_zone" "fail3" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = [""]
}
resource "panos_panorama_zone" "fail4" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = [""]
}

# User-ID enabled, Include ACL defined, string of spaces in list
resource "panos_zone" "fail5" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["    "]
}
resource "panos_panorama_zone" "fail6" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
    enable_user_id = true
    include_acls = ["    "]
}
