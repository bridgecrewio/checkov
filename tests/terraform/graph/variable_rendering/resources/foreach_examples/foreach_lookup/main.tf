resource "google_storage_bucket" "buckets_upper" {
  for_each = var.names

  uniform_bucket_level_access = lookup(
    var.bucket_policy_only,
    upper(each.value),
    true,
  )
}

resource "google_storage_bucket" "buckets_lower" {
  for_each = var.names

  uniform_bucket_level_access = lookup(
    var.bucket_policy_only,
    lower(each.value),
    true,
  )
}

variable "bucket_policy_only" {
  description = "Disable ad-hoc ACLs on specified buckets. Defaults to true. Map of lowercase unprefixed name => boolean"
  type        = map(bool)
  default     = {}
}

variable "names" {
  description = "Bucket name suffixes."
  type        = list(string)
  default = ["a"]
}