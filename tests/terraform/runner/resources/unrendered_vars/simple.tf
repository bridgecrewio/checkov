variable "bucket" {
  default = "xyz"
}

resource "aws_s3_bucket" "unknown_simple" {
  bucket = var.unknown_bucket
}

resource "aws_s3_bucket" "known_simple_pass" {
  bucket = var.bucket
}
