variable "unscoped_private_acl" {
  default = "private"
}

variable "unscoped_public_read_write_acl" {
  default = "public-read-write"
}

locals {
  unscoped_private_acl = "private"
  unscoped_public_read_write_acl = "public-read-write"
}