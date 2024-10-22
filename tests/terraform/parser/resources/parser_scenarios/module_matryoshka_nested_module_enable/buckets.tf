module "bucket1" {
  source   = "./bucket1"
}

resource "aws_s3_bucket" "example0" {
  bucket = "bucket0"
}