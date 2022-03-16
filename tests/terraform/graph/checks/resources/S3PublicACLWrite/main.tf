# pass

resource "aws_s3_bucket" "private_acl" {
  bucket = "example"

  acl = "private"
}

resource "aws_s3_bucket" "no_acl" {
  bucket = "example_no_acl"
}

resource "aws_s3_bucket" "unknown_var" {
  bucket = "example"

  acl = var.unknown_var
}

variable "unknown_var" {
  description = "unknown value"
}

# fail

resource "aws_s3_bucket" "public_read_write" {
  bucket = "example"
  acl = "public-read-write"
}

# provider version 4

# pass
resource "aws_s3_bucket" "private_acl_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "private_acl_v4" {
  bucket = aws_s3_bucket.private_acl_v4.id
  acl = "private"
}

# fail

resource "aws_s3_bucket" "public_read_write_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "public_read_write_v4" {
  bucket = aws_s3_bucket.public_read_write_v4.id
  acl = "public-read-write"
}