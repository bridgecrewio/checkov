resource "aws_s3_bucket_object" "this_file" {
  for_each = var.file_map_level2
  bucket   = "your_bucket_name"
  key      = each.key
  source   = each.value
}
