# From: https://www.terraform.io/docs/configuration/modules.html#multiple-instances-of-a-module

module "bucket" {
  for_each = toset(["assets", "media"])
  source   = "./publish_bucket"
  name     = "${each.key}_bucket"
}