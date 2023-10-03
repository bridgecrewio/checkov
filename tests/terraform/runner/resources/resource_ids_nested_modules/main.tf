provider "aws" {
  region  = "us-west-2"
}

module "s3_module" {
  source = "./module"
  acl    = "public-read"
}

module "recursive_module" {
  source = "./"
}

resource "aws_s3_bucket" "example" {
  bucket = "example"
  acl    = "public-read"
}

