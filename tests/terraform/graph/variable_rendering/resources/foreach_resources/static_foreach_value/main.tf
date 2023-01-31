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

resource "aws_s3_bucket" "bucket_map_rendered" {
  for_each = {var.a: var.a, "key2": var.b}
  bucket   = each.value
}

resource "aws_s3_bucket" "count_static" {
  count  = 5
  bucket = count.index
}

resource "aws_s3_bucket" "count_rendered" {
  count = var.a
  bucket   = count.index
}

resource "aws_s3_bucket" "count_rendered_length" {
  count = length(var.files)
  bucket   = count.index
}