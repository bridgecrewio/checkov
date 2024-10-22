module "bucket" {
  source   = "./bucket"
  name     = "my_bucket1"
}

module "bucket2" {
  source   = "./bucket"
  name     = "my_bucket2"
}