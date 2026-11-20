variable "dnssec_key_spec" {
  type = object({
    algorithm  = optional(string)
    key_length = optional(number)
    key_type   = optional(string)
  })
}

resource "google_dns_managed_zone" "unknown" {
  name     = "example-zone"
  dns_name = "example.com."

  dynamic "dnssec_config" {
    for_each = [var.dnssec_key_spec]

    content {
      dynamic "default_key_specs" {
        for_each = [dnssec_config.value]

        content {
          algorithm  = default_key_specs.value.algorithm
          key_length = default_key_specs.value.key_length
          key_type   = default_key_specs.value.key_type
        }
      }
    }
  }
}
