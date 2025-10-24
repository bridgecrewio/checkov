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

locals {
  names = ["bad_example", "terrible_example", "awful_example"]
}

module "sg" {
  # checkov:skip=CKV_AWS_277
  for_each = toset(local.names)
  name     = each.value
  source   = "./modules/ec2/security_group"
  vpc_id   = var.vpc_id
}