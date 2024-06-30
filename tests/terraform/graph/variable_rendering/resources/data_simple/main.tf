data "aws_s3_bucket" "data_list" {
  for_each = toset(var.test_list.bucket)
  bucket = each.value
}

data "aws_s3_bucket" "data_dict" {
  for_each = var.test_dict.bucket
  bucket = each.value
}

data "aws_s3_bucket" "data_count" {
  count = var.test_count.bucket
  bucket = count.index
}