locals {
  hosted_zone_names = [
    "example.com",
    "example2.eu",
  ]
}

resource "aws_route53_zone" "example" {
  for_each = toset(local.hosted_zone_names)
  # checkov:skip=CKV2_AWS_38
  name = each.value
}