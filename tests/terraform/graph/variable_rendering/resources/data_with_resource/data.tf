data "aws_s3_bucket" "data_dict" {
  for_each = var.test_dict.bucket
  bucket = "a"
}

data "aws_s3_bucket" "data_count" {
  count = var.test_count.bucket
  bucket = count.index
}

data "aws_s3_bucket" "data" {
  bucket = "a"
}