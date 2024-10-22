module "bucket2" {
  source   = "./bucket2"
}

resource "aws_s3_bucket" "example1" {
  bucket = "bucket1"
}