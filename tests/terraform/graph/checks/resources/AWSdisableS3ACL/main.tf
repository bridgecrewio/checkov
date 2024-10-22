# FAIL

resource "aws_s3_bucket" "pud_bucket_fail" {
  bucket = "pud_bucket_fail"
}

resource "aws_s3_bucket_ownership_controls" "pud_bucket_fail" {
  bucket = aws_s3_bucket.pud_bucket_fail.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# PASS

resource "aws_s3_bucket" "pud_bucket_pass" {
  bucket = "pud_bucket_pass"
}

resource "aws_s3_bucket_ownership_controls" "pud_bucket_pass" {
  bucket = aws_s3_bucket.pud_bucket_pass.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}