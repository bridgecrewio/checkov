provider "aws" {
  region = "usw2"
}

provider "aws" {
  alias = "usw1"
  region = ""
}

resource "aws_s3_bucket" "bucket"{
  bucket = "bucket"
  provider = aws.usw1
}

resource "aws_s3_bucket" "bucket_2" {
  bucket = "bucket-2"
}