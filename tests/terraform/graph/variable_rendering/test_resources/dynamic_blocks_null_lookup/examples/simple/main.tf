module "secgrp-1" {
  source = "../../"
  name   = "project-abc"

  vpc_id  = var.vpc_id
  ingress = var.ingress
  egress  = var.egress

  tags = {
    Tier       = "Application"
    Allocation = "1234"
  }
}
