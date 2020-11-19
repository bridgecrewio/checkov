output "bucket_name" {
  value = aws_s3_bucket.example.bucket
}

resource "aws_s3_bucket" "example" {
  bucket = "my_bucket"
}