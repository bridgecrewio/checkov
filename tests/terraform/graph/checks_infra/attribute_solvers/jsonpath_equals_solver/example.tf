resource "aws_security_group" "web-node" {
  # security group is open to the world in SSH port
  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
}