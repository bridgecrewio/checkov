provider "aws" {
  region = "aaa"
}

module "s3_module" {
  for_each = ["a", "b"]
  source = "./module"
  bucket = false
}