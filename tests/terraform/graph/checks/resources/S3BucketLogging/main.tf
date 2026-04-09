resource "aws_s3_bucket" "bucket_good_1" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "bucket_good_2" {
  bucket = "bucket_good"

  logging {
    target_bucket = aws_s3_bucket.log_bucket.id
    target_prefix = "log/"
  }
}

resource "aws_s3_bucket_logging" "example" {
  bucket = aws_s3_bucket.bucket_good_1.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}

resource "aws_s3_bucket" "bucket_bad_1" {
  bucket = "bucket_bad_1"
}

resource "aws_s3_bucket" "bucket_good_count" {
  count  = 1
  bucket = "bucket_good_count"
}

resource "aws_s3_bucket_logging" "count_logging" {
  bucket        = aws_s3_bucket.bucket_good_count[0].id
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}

resource "aws_s3_bucket" "bucket_bad_count" {
  count  = 1
  bucket = "bucket_bad_count"
}

resource "aws_s3_bucket" "bucket_good_multi_count" {
  count  = 2
  bucket = "bucket_good_multi_count_${count.index}"
}

resource "aws_s3_bucket_logging" "multi_count_logging" {
  count         = 2
  bucket        = aws_s3_bucket.bucket_good_multi_count[count.index].id
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}
