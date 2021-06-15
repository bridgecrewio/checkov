# pass
resource "aws_s3_bucket" "passed_bucket" {
  bucket = "passed_bucket"
  acl    = var.private_acl
}

# fail
resource "aws_s3_bucket" "failed_bucket" {
  bucket = "failed_bucket"
  acl    = var.public_read_write_acl
}

# unknown
resource "aws_s3_bucket" "unknown_acl_bucket" {
  bucket = "unknown_acl_bucket"
  acl    = var.var_doesnt_exist
}

resource "aws_s3_bucket" "unknown_acl_bucket_2" {
  bucket = "unknown_acl_bucket_2"
  acl    = var.unscoped_private_acl
}

resource "aws_s3_bucket" "unknown_acl_bucket_3" {
  bucket = "unknown_acl_bucket_3"
  acl    = var.unscoped_public_read_write_acl
}

resource "aws_s3_bucket" "unknown_acl_bucket_4" {
  bucket = "unknown_acl_bucket_4"
  acl    = local.unscoped_private_acl
}

resource "aws_s3_bucket" "unknown_acl_bucket_5" {
  bucket = "unknown_acl_bucket_5"
  acl    = local.unscoped_public_read_write_acl
}