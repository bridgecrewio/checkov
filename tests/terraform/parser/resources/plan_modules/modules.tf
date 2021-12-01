module "mymodule_1" {
  source = "./mymodule"
  for_each = toset(["foo", "bar"])
}

module "mymodule_2" {
  source = "./mymodule"
}
