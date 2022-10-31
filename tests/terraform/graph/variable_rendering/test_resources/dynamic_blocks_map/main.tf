

resource "aws_security_group" "list_example" {
 name        = "list-example"
  dynamic "ingress" {
    for_each = var.ports
    content {
      protocol    = ingress.value["protocol"]
      from_port   = ingress.value["inbound_ports"]
      to_port     = ingress.value["inbound_ports"]
      cidr_blocks = ["0.0.0.0/0"]
     }
   }

 dynamic "egress" {
    for_each = var.ports
    content {
      protocol    = egress.value["protocol"]
      from_port   = egress.value["outbound_ports"]
      to_port     = egress.value["outbound_ports"]
      cidr_blocks = ["0.0.0.0/0"]
     }
   }
}
