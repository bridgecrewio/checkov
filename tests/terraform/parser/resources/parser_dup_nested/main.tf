provider "aws" {
  region  = "us-west-2"
  alias = "test_provider"
  test_provider = True
}

module "s3_module" {
  source = "./module"
  bucket = false
  bucket2 = ""
}

module "s3_module2" {
  source = "./module"
  bucket = ""
  bucket2 = true
}