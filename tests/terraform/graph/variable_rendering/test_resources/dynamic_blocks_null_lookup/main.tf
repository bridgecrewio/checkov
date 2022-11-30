resource "aws_security_group" "this" {
  count       = var.vpc_id != "" ? 1 : 0
  name        = format("%s-sg", var.name)
  description = format("Security Group for %s", var.name)
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress
    content {
      cidr_blocks      = lookup(ingress.value, "cidr_blocks", null)
      ipv6_cidr_blocks = lookup(ingress.value, "ipv6_cidr_blocks", null)
      prefix_list_ids  = lookup(ingress.value, "prefix_list_ids", null)
      from_port        = lookup(ingress.value, "from_port")
      to_port          = lookup(ingress.value, "to_port")
      protocol         = lookup(ingress.value, "protocol", "tcp")
      security_groups  = lookup(ingress.value, "security_groups", null)
      self             = lookup(ingress.value, "self", false)
      description      = lookup(ingress.value, "description")
    }
  }

  dynamic "egress" {
    for_each = var.egress
    content {
      cidr_blocks      = lookup(egress.value, "cidr_blocks", null)
      ipv6_cidr_blocks = lookup(egress.value, "ipv6_cidr_blocks", null)
      prefix_list_ids  = lookup(egress.value, "prefix_list_ids", null)
      from_port        = lookup(egress.value, "from_port")
      to_port          = lookup(egress.value, "to_port")
      protocol         = lookup(egress.value, "protocol", "tcp")
      security_groups  = lookup(egress.value, "security_groups", null)
      self             = lookup(egress.value, "self", false)
      description      = lookup(egress.value, "description")
    }
  }

  tags = merge(
    {
      Name = format("%s-sg", var.name)
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }

}