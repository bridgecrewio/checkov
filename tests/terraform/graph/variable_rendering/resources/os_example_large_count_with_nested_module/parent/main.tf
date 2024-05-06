# parent/main.tf
variable "parent" {
  type = string
}
module "parent" {
  source = "../child"
  child-name   = "1"
}

output "parent-result" {
  value = module.parent.child-result
}