
module "simple" {
  source = "./simple"
  bucket = "my_bucket"
  key    = "my_key"
  count  = 2
  # checkov:skip=CKV_AWS_88:Testing
}