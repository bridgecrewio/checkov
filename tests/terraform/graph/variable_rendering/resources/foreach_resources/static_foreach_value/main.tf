resource "aws_s3_bucket" "bucket_static_set" {
  for_each = toset(["bucket_a", "bucket_b"])
  bucket   = each.value
}

resource "aws_s3_bucket" "bucket_static_map" {
  for_each = {"key1": var.a, "key2": var.b}
  bucket   = each.value
}

resource "aws_s3_bucket" "bucket_rendered" {
  for_each = var.a
  bucket   = each.value
}