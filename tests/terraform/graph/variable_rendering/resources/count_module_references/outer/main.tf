variable "bucket_id" {}

module "inner" {
  source    = "../takes_input"
  bucket_id = var.bucket_id
}
