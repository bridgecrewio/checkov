resource "aws_s3_bucket_object" "this_file" {
  source   = "readme.md"
}

resource "aws_s3_bucket" "my_bucket" {
}