resource "aws_s3_bucket" "bucket_good_1" {
  bucket = "bucket_good"
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