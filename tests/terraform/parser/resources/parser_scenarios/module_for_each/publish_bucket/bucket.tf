variable "name" {}

resource "aws_s3_bucket" "example" {
  bucket = var.name
}