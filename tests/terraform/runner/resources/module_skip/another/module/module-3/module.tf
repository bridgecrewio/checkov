# Bucket that will fail (no encryption) defined INSIDE a module
resource "aws_s3_bucket" "nested-inside" {
  bucket = "nested-inside-bucket"
}
