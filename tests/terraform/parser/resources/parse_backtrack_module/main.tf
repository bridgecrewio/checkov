variable "bucket_name" {
  type = string
}

resource "aws_s3_bucket" "root" {
  bucket = var.bucket_name
}