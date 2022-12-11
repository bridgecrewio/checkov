resource "aws_s3_bucket" "example3" {
  bucket = "bucket3"
  acl    = "public-read"      # used by test_runner.py
}