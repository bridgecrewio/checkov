variable "v" {
  default = true
}

module "module1" {
  source = "./module1"
  v = var.v
}

module "module2" {
  source = "./module2"
  v = var.v
}