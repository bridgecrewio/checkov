variable "name" {}

locals {
  MODULE_TAIL = "bucket"
}

output "bucket_name" {
  value = aws_s3_bucket.example.bucket
}

resource "aws_s3_bucket" "example" {
  bucket = "${var.name}-${local.MODULE_TAIL}"
}