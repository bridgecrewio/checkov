resource "google_dns_managed_zone" "private1" {
  # No result because visibility is private
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "private"

}

resource "google_dns_managed_zone" "private2" {
  # No result because visibility is private
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "private"

  dnssec_config {
    state = "on"
  }

}

resource "google_dns_managed_zone" "private3" {
  # No result because visibility is private
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "private"

  dnssec_config {
    state = "off"
  }

}

resource "google_dns_managed_zone" "pass1" {
  # Pass because visibility is public and value is set
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "public"

  dnssec_config {
    state = "on"
  }

}

resource "google_dns_managed_zone" "pass2" {
  # Pass because visibility is public (by default) and value is set
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  dnssec_config {
    state = "on"
  }

}

resource "google_dns_managed_zone" "fail1" {
  # Fail because visibility is public and dnssec block is missing
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "public"

}

resource "google_dns_managed_zone" "fail2" {
  # Fail because visibility is public and value is off
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  visibility = "public"
  dnssec_config {
    state = "off"
  }
}

resource "google_dns_managed_zone" "fail3" {
  # Fail because visibility is public (by default) and value is off
  name        = "zone"
  dns_name    = "services.example.com."
  description = "Example DNS Service Directory zone"

  dnssec_config {
    state = "off"
  }
}