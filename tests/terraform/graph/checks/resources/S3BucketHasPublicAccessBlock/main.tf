resource "aws_s3_bucket" "bucket_good_1" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "bucket_good_2" {
  count  = var.cur_bucket_name != "" ? 1 : 0
  bucket = "bucket_good_2"
}

resource "aws_s3_bucket" "bucket_bad_1" {
  bucket = "bucket_bad_1"
}

resource "aws_s3_bucket" "bucket_bad_2" {
  bucket = "bucket_bad_2"
}

resource "aws_s3_bucket" "bucket_bad_3" {
  bucket = "bucket_bad_3"
}

resource "aws_s3_bucket" "bucket_bad_4" {
  bucket = "bucket_bad_4"
}

resource "aws_s3_bucket_public_access_block" "access_good_1" {
  bucket = aws_s3_bucket.bucket_good_1.id

  block_public_acls   = true
  block_public_policy = true
}

// Test for checkov failing to find the associated public_access_block resource when 'count' is used.
// checkov 3.2.478 fixed this in https://github.com/bridgecrewio/checkov/pull/7303/files#diff-77c177a4c101efaf3685daff654840ef935d65f190afb9e1b68bae198b3b56f5
resource "aws_s3_bucket_public_access_block" "access_good_2" {
  count                   = var.cur_bucket_name != "" ? 1 : 0
  bucket                  = aws_s3_bucket.bucket_good_2[0].id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_public_access_block" "access_bad_1" {
  bucket = aws_s3_bucket.bucket_bad_1.id
}

resource "aws_s3_bucket_public_access_block" "access_bad_2" {
  bucket = aws_s3_bucket.bucket_bad_2.id

  block_public_acls   = false
  block_public_policy = false
}

resource "aws_s3_bucket_public_access_block" "access_bad_3" {
  bucket = aws_s3_bucket.bucket_bad_3.id

  block_public_acls   = false
  block_public_policy = true
}