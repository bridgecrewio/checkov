locals {
  default_tags = {
    a        = var.a
    b        = var.b
    c        = var.c
    d        = local.d
  }
#  default_tags2 = {
#    role2        = var.role2
#  }
}

resource "aws_ecs_cluster" "cluster" {
#  tags = local.default_tags
  tags = merge(local.default_tags)
}