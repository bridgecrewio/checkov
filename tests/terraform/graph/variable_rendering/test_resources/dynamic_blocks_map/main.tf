resource "aws_network_acl" "network_acl" {
  vpc_id = data.aws_vpc

  dynamic "ingress" {
    for_each = var.http_headers
    content {
      rule_no    = ingress.value.num
      protocol   = ingress.value.protoc
      action     = "allow"
      cidr_block = ingress.value.values
      from_port  = 22
      to_port    = 22
    }
  }
}