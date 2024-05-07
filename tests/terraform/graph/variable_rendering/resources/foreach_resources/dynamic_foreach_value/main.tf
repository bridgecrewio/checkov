provider "aws" {
  region = "us-west-1"
}

provider "abbey" {
  alias = "a"
  region = ""
}

locals {
  name_map = var.names_map
  name_list = var.names_list
  count = var.number
  count_list = var.names_list
}

resource "aws_s3_bucket" "bucket_rendered" {
  for_each = local.name_map
  name     = each.key
  location = each.value
  region = var.test
  provider = abbey.a
}

resource "aws_s3_bucket" "bucket_map_rendered" {
  for_each = local.name_list
  bucket   = each.value
}

resource "aws_s3_bucket" "count_rendered" {
  count  = local.count
  bucket = count.index
}

resource "aws_s3_bucket" "count_rendered_length" {
  count = length(local.count_list)
  bucket   = count.index
}

resource "aws_s3_bucket" "not_foreach" {
  for_each = local.wrong
}

resource "aws_s3_bucket" "not_foreach" {
  region = var.test
}

resource "aws_s3_bucket" "not_foreach" {
  region = local.count_list
}

resource "aws_s3_bucket" "not_foreach" {
  region = local.count_list
}
