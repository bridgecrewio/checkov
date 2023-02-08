resource "aws_s3_bucket" "foreach_map" {
  for_each = var.foreach_map
  name     = each.value
  region   = each.key
  location = var.test
}