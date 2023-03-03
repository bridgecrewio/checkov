module "inner_s3_module" {
  source = "../module2"
  bucket2 = var.bucket
}

module "inner_s3_module_2" {
  source = "../module2"
  bucket2 = var.bucket
}
