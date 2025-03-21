resource "aws_s3_bucket" "fail" {
  bucket = "company-data-storage-2024"
}

resource "aws_s3_access_point" "fail" {
  bucket = aws_s3_bucket.vulnerable_bucket.id
  name   = "analytics-endpoint"

  public_access_block_configuration {
    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
  }

  vpc_configuration {
    vpc_id = "vpc-0a1b2c3d4e5f6g7h8"
  }
}
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "secure-data-storage-2024"
}

resource "aws_s3_access_point" "pass" {
  bucket = aws_s3_bucket.secure_bucket.id
  name   = "internal-endpoint"

  public_access_block_configuration {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }

  vpc_configuration {
    vpc_id = "vpc-0a1b2c3d4e5f6g7h8"
  }
}