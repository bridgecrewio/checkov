
resource "aws_s3_bucket_object" "this_file_2" {
  bucket   = "your_bucket_name"
  key = "some_key"
}