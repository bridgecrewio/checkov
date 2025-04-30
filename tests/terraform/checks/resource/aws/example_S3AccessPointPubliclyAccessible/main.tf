resource "aws_s3_bucket" "example" {
  bucket = "example"
}

resource "aws_s3_access_point" "example_pass" {
  bucket = aws_s3_bucket.example.id
  name   = "example"
  public_access_block_configuration = public_access_block_configuration.pass
}

resource "aws_s3_access_point" "example_fail" {
  bucket = aws_s3_bucket.example.id
  name   = "example"
  public_access_block_configuration = public_access_block_configuration.fail
}

resource "aws_s3_account_public_access_block" "pass1" {
  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_account_public_access_block" "pass2" {
  block_public_acls   = true
  restrict_public_buckets = true
}

resource "aws_s3_account_public_access_block" "fail" {
  block_public_acls   = true
  restrict_public_buckets = false
}