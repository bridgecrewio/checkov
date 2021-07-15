resource "aws_s3_bucket" "some-bucket" {
  bucket = "my-bucket"
}

output "o1" {
  value = aws_s3_bucket.some-bucket.arn
}