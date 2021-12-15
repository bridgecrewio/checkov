resource "aws_s3_bucket" "mod_bucket" {
  bucket        = "example"

  versioning {
    enabled = var.versioning
  }
}

variable "versioning" {
  type = bool
}
