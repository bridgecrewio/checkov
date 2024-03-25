resource "aws_s3_bucket_object" "this_file" {
  bucket   = "your_bucket_name"
  key      = "readme.md"
  source   = "readme.md"
}
