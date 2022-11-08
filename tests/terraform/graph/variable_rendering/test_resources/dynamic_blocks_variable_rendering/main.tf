resource "aws_security_group" "list_example" {
 name        = "list-example"

 dynamic "ingress" {
   for_each = var.dynamic.inbound_ports
   content {
     from_port   = ingress.value
     to_port     = ingress.value
     protocol    = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }

 dynamic "egress" {
   for_each = var.dynamic.outbound_ports
   content {
     from_port   = egress.value
     to_port     = egress.value
     protocol    = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }
}

resource "aws_security_group" "single_dynamic_example" {
 name        = "list-example"

 dynamic "ingress" {
   for_each = var.dynamic.inbound_ports
   content {
     from_port   = ingress.value
     to_port     = ingress.value
     protocol    = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }
}

