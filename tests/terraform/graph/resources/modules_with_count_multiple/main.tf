module "security_group" {
  count  = 2
  source = "./module"
  name   = "sg-${count.index}"
}

resource "aws_lb" "zero" {
  name            = "zero"
  security_groups = [module.security_group[0].security_group_id]
  subnets         = ["subnet-1"]
}

resource "aws_lb" "one" {
  name            = "one"
  security_groups = [module.security_group[1].security_group_id]
  subnets         = ["subnet-1"]
}
