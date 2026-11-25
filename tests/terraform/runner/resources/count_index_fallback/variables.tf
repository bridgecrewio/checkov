variable "other_mode" {
  type    = string
  default = "required"
  validation {
    condition     = contains(["required", "optional"], var.other_mode)
    error_message = "other_mode must be required or optional."
  }
}
variable "enable_other" {
  type    = bool
  default = true
}
variable "other_secret_ref" {
  type = object({
    name = string
  })
  default = null
  validation {
    condition     = var.other_secret_ref == null || var.other_secret_ref.name != ""
    error_message = "other_secret_ref is used by aws_elasticache_replication_group.widget and must have a name."
  }
}
variable "target_enabled" {
  type    = bool
  default = false
}
variable "target_image" {
  type        = string
  default     = "example/app:1.0.0@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  description = "Image for the target. Only deployed when local.b is true."
}
