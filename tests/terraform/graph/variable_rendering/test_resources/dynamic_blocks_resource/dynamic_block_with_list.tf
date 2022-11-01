locals {
 inbound_ports  = [80, 443]
 outbound_ports = [443, 1433]
}

resource "aws_security_group" "list_example" {
 name        = "list-example"

 dynamic "ingress" {
   for_each = local.inbound_ports
   content {
     from_port   = ingress.value
     to_port     = ingress.value
     protocol    = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }

 dynamic "egress" {
   for_each = local.outbound_ports
   content {
     from_port   = egress.value
     to_port     = egress.value
     protocol    = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }
}
