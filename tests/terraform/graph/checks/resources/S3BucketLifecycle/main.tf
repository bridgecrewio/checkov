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

# provider v3

resource "aws_s3_bucket" "pass_v3" {
  bucket = "bucket_good"

  lifecycle_rule {
    id                                     = "Delete old incomplete multi-part uploads"
    enabled                                = true
    abort_incomplete_multipart_upload_days = 7
  }
}
