module "security_group" {
  for_each = toset(["alpha", "beta"])
  source   = "./module"
  name     = "sg-${each.key}"
}

resource "aws_lb" "alpha" {
  name            = "alpha"
  security_groups = [module.security_group["alpha"].security_group_id]
  subnets         = ["subnet-1"]
}

resource "aws_lb" "beta" {
  name            = "beta"
  security_groups = [module.security_group["beta"].security_group_id]
  subnets         = ["subnet-1"]
}
