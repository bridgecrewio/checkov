variable "create_sg" {
  default = true
}

module "security_group" {
  count  = var.create_sg ? 1 : 0
  source = "./module"
  name   = "alb-sg"
}

resource "aws_lb" "alb" {
  name            = "example"
  security_groups = [module.security_group[0].security_group_id]
  subnets         = ["subnet-1", "subnet-2"]
}
