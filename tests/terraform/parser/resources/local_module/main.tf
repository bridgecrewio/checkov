module "mod" {
  source = "./module"
  versioning = true
}

module "mod2" {
  source = "./module"
  versioning = false
}
