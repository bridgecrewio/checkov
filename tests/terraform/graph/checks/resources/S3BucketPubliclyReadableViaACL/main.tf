# Create S3 bucket
resource "aws_s3_bucket" "fail" {
  bucket = "my-website-bucket"
}

# Block public access at bucket level
resource "aws_s3_bucket_public_access_block" "fail_block" {
  bucket = aws_s3_bucket.fail.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Set bucket ACL
resource "aws_s3_bucket_acl" "website_bucket_acl" {
  depends_on = [aws_s3_bucket_public_access_block.fail_block]

  bucket = aws_s3_bucket.fail.id
  acl    = "private"
}

# Block public access at account level
resource "aws_s3_account_public_access_block" "account_block" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Website configuration
resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.fail.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# Create S3 bucket
resource "aws_s3_bucket" "pass" {
  bucket = "my-website-bucket"
}

# Block public access at bucket level
resource "aws_s3_bucket_public_access_block" "block_pass" {
  bucket = aws_s3_bucket.pass.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Set bucket ACL
resource "aws_s3_bucket_acl" "website_bucket_acl1" {
  depends_on = [aws_s3_bucket_public_access_block.pass]

  bucket = aws_s3_bucket.pass.id
  acl    = "private"
}

# Block public access at account level
resource "aws_s3_account_public_access_block" "account_block1" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Website configuration
resource "aws_s3_bucket_website_configuration" "website1" {
  bucket = aws_s3_bucket.pass.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}