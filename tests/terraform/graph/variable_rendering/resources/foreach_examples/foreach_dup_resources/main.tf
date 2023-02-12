resource "aws_s3_bucket" "foreach_map" {
  for_each = var.foreach_map
  name     = each.value
  region   = each.key
}

resource "aws_s3_bucket" "foreach_list" {
  for_each = toset(var.foreach_list)
  name     = each.value
  region   = each.key
}

resource "aws_s3_bucket" "static_resource" {
  name     = "name"
  region = "region"
}