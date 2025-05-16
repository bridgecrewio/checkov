resource "aws_s3_access_point" "pass" {
  bucket = aws_s3_bucket.example.id
  name   = "example-access-point"

  public_access_block_configuration {
    block_public_acls       = true
    ignore_public_acls      = true
    block_public_policy     = true
    restrict_public_buckets = true
  }
}

resource "aws_s3_access_point" "pass_missing" {
  bucket = aws_s3_bucket.example.id
  name   = "example-access-point"
}

resource "aws_s3_access_point" "fail" {
  bucket = aws_s3_bucket.example.id
  name   = "example-access-point"

  public_access_block_configuration {
    block_public_acls       = false
    ignore_public_acls      = false
    block_public_policy     = false
    restrict_public_buckets = false
  }
}