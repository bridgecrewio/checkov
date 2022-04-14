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
