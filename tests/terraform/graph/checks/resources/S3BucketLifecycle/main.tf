resource "aws_s3_bucket" "pass" {
  bucket = "bucket_good"
}


resource "aws_s3_bucket_lifecycle_configuration" "pass" {
  bucket = aws_s3_bucket.pass.id
  rule {
    id     = ""
    status = ""
  }
}

resource "aws_s3_bucket" "fail" {
  bucket = "bucket_bad_1"
}
