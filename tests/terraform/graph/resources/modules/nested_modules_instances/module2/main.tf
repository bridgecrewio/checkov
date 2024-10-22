module "inner_s3_module2" {
  source = "../module3"
  bucket2 = var.bucket2
}
