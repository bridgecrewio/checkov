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

// resource in the tfplan.json file that is missing in the terraform
//resource "aws_s3_bucket" "example_2" {
//  bucket = "example_2"
//}