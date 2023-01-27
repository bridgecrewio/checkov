resource "aws_s3_bucket" "bucket" {
  for_each = toset(["bucket_a", "bucket_b"])
  bucket   = each.value
}