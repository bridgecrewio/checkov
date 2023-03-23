provider "aws" {
  region  = "us-west-2"
  alias = "test_provider"
  test_provider = True
}

module "s3_module" {
  for_each = var.foreach_var
  source = "./module"
  bucket = false
  bucket2 = ""
}

module "s3_module2" {
  count = var.count_var
  source = "./module"
  bucket = ""
  bucket2 = true
}