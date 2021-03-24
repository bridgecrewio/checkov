variable "enabled" {
  default = module.learn_terraform.region == "something to produce false" ? true : false
}
