variable "config" {
  type = any
  default = {
    abort_incomplete_multipart_upload = 7
    storage_class                     = "STANDARD_IA"
  }
}

variable "bucket_transition_lifecycle_rule" {
  type = list(map(any))
  default = [{
    "id"                                     = "set-to-ia"
    "status"                                 = "Disabled"
    "abort_incomplete_multipart_upload_days" = 7
  }]
}

variable "versioning" {
  type    = bool
  default = true
}

variable "expire_days" {
  type    = number
  default = 30
}

locals {
  lifecycle_rules = {
    storage_class = ["STANDARD_IA"]
  }
}
