provider "aws" {
  region  = "us-west-2"
  alias = "test_provider"
  test_provider = True
}

module "s3_module" {
  source = "./module"

  bucket = aws_s3_bucket.example.id
}


resource "aws_s3_bucket" "example" {
  bucket = "example"
}

