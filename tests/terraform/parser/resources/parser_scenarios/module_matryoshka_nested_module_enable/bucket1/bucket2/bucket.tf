module "bucket3" {
  source   = "./bucket3"
}

resource "aws_s3_bucket" "example2" {
  bucket = "bucket2"
}