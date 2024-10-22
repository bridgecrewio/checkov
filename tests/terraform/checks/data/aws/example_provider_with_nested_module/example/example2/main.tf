provider "abbey" {
}

provider "aws" {
 region = ""
 alias = "aaa"
}

resource "aws_s3_bucket" "bucket"{
 bucket = "module-bucket"
 provider = "aws.aaa"
}