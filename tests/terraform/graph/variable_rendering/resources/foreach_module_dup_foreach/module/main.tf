module "inner_s3_module" {
  for_each = ["c", "d"]
  source = "./module2"
  bucket2 = var.bucket
}

module "inner_s3_module2" {
  for_each = ["e", "f"]
  source = "./module2"
  bucket2 = var.bucket2
}


variable "bucket" {
  type = string
}

variable "bucket2" {
  type = string
}