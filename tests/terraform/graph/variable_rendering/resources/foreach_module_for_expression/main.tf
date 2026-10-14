variable "items" {
  type    = list(string)
  default = ["a", "b"]
}

module "child" {
  source   = "./module"
  for_each = { for v in var.items : v => v }
  val      = each.value
}
