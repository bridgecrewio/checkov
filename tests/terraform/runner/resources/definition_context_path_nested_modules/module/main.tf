module "inner_s3_module" {
  source = "./module2"
  acl    = var.acl
}

resource "aws_s3_bucket" "example2" {
  bucket = "example"
  acl    = var.acl
}