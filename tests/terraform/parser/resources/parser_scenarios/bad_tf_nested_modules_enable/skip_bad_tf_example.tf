variable "okay" {
}

// Variable is missing a name, not valid terraform syntex
variable {
  name    = "test"
  default = "test_value"
  type    = "string"
}

module "bar" {
    memory = "1G"
    source = "baz"
}

module "okay" {
  source = "./okay"
  source = "baz2"
}

// Module is missing a name, can't be referenced or deployed
module {
  source = "./not-okay"
  memory = "far"
}
