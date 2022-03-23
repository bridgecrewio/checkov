# The "zone_profile" attributes can be defined in either the "panos_zone" or "panos_panorama_zone" resources.
# All these resource types are covered by this check.

# Passes

# Zones should should have a "zone_profile" populated to protect against provide extended protection against IP floods, reconnaissance, packet based attacks, etc
resource "panos_zone" "pass1" {
    name = "new_zone"
    zone_profile = "zone_protect_profile"
}
resource "panos_panorama_zone" "pass2" {
    name = "new_zone_panorama"
    zone_profile = "zone_protect_profile"
}

# Fails

# Zones should should have a "zone_profile" populated to protect against provide extended protection against IP floods, reconnaissance, packet based attacks, etc - lack of "zone_profile" attribute is a fail
resource "panos_zone" "fail1" {
    name = "new_zone"
}
resource "panos_panorama_zone" "fail2" {
    name = "new_zone_panorama"
}

# Zones should should have a "zone_profile" populated to protect against provide extended protection against IP floods, reconnaissance, packet based attacks, etc - empty string "zone_profile" attributes are a fail
resource "panos_zone" "fail3" {
    name = "new_zone"
    zone_profile = ""
}
resource "panos_panorama_zone" "fail4" {
    name = "new_zone_panorama"
    zone_profile = ""
}

# Zones should should have a "zone_profile" populated to protect against provide extended protection against IP floods, reconnaissance, packet based attacks, etc - strings of space characters for "zone_profile" attributes are a fail
resource "panos_zone" "fail5" {
    name = "new_zone"
    zone_profile = "   "
}
resource "panos_panorama_zone" "fail6" {
    name = "new_zone_panorama"
    zone_profile = "   "
}
