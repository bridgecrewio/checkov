provider "aws" {
  region  = "us-west-2"
}

module "s3_module" {
  source = "./module"

  bucket = aws_s3_bucket.example.id
}

module "s3_module2" {
  source = "./module"

  bucket = aws_s3_bucket.example2.id
}

resource "aws_s3_bucket" "example" {
  bucket = "example"
}

resource "aws_s3_bucket" "example2" {
  bucket = "example"
}
