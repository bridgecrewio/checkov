# Example HCL2 syntax that won't parse in HCL1
# (from https://github.com/virtuald/pyhcl/issues/74)

locals {
  map = {
    r1 = "21.0.0.0/16"
    r2 = "22.4.0.0/16"
  }

  sg = {
    "test" = [
      "r1",
      "r2"
    ]
  }

}

resource "aws_security_group" "test" {
  name   = "test"
  vpc_id = "vpc-xxxxxxxxx"

  dynamic "ingress" {
    for_each = local.sg.test
    content {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = split(",", lookup(local.map, ingress.value, ingress.value))
    }
  }
}