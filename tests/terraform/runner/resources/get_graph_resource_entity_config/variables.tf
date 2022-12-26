variable "versioning_enabled" {
  type        = bool
  default     = false
  description = "A state of versioning. Versioning is a means of keeping multiple variants of an object in the same bucket"
}

variable "company_name" {
  default = "acme"
}

variable "environment" {
  default = "dev"
}

data "aws_caller_identity" "current" {}
