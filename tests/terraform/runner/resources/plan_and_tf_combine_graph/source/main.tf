provider "aws" {
  region  = "us-west-2"
  profile = "dev8"
}

module "s3_module" {
  source = "./module"

  bucket = aws_s3_bucket.example.id
}

resource "aws_s3_bucket" "example" {
  bucket = "example"
}

module "s3_module_2" {
  source = "./module"

  bucket = aws_s3_bucket.example_2.id
}

resource "aws_s3_bucket" "example_2" {
  bucket = "example_2"
}
