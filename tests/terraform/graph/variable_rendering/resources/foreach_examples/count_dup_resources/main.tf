locals {
  name_count = var.name_count
}

resource "aws_s3_bucket" "count_var_resource" {
  count = local.name_count
  name     = count.index
  region = var.test
}

resource "aws_s3_bucket" "var_resource" {
  name     = "name"
  region = var.test
}

resource "aws_s3_bucket" "static_resource" {
  name     = "name"
  region = "region"
}