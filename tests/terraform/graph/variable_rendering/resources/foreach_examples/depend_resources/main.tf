resource "aws_s3_bucket" "foreach_map" {
  for_each = var.foreach_map
  name     = each.key
  region   = each.value
  location = var.test
}