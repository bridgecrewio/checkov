# resource with same name as a failed resource
resource "aws_s3_bucket" "public_read" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "this_is_me" {
  bucket = aws_s3_bucket.public_read.id
  acl = "private"
}