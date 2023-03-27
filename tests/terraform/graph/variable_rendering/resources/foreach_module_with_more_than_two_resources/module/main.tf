module "inner_s3_module" {
  count = 4
  source = "./module2"
  bucket2 = var.bucket
}

module "inner_s3_module2" {
  for_each = ["a", "b", "c"]
  source = "./module2"
  bucket2 = var.bucket2
}


variable "bucket" {
  type = string
}

variable "bucket2" {
  type = string
}