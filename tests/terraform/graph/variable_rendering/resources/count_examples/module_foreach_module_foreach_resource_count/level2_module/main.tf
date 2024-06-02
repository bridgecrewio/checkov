resource "aws_s3_bucket_object" "this_file" {
  count = var.times_to_duplicate_bucket
  bucket   = "your_bucket_name"
  key      = each.key
  source   = each.value
}
