module "another_s3_module" {
  source = "../module3"

  bucket = aws_s3_bucket.example_another.id
}

resource "aws_s3_bucket" "example_another" {
  bucket = "example_another"
}