locals {
  default_tags = {
    a        = var.a
    b        = var.b
    c        = var.c
    d        = local.d
  }
}

resource "aws_ecs_cluster" "cluster" {
#  tags = local.default_tags
  tags = merge(local.default_tags)
}