locals {
  common_tags = {
    Tag1 = "one"
    Tag2 = "two"
  }

  one_arg_local = merge(local.common_tags)

}
