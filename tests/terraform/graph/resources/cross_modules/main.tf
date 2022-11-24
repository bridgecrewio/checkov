module "test" {
  source = "./module"
  bucket = aws_s3_bucket.example.id
}

resource "aws_s3_bucket" "example" {
  bucket = "example"
}