module "inner_s3_module" {
  source = "../module2"
  bucket2 = var.bucket
}
