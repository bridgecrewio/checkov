resource "aws_security_group" "sg1" {
  description = "sg1"

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0", "25.0.9.19/92"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description     = "Access to Bastion Host Security Group"
    from_port       = "5432"
    protocol        = "tcp"
    security_groups = ["sg-id-0"]
    self            = "false"
    to_port         = "8182"
  }
}

resource "aws_security_group" "sg2" {
  description = "security_group_2"

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description     = "Access to  SG"
    from_port       = "5432"
    protocol        = "tcp"
    security_groups = ["sg-id-0"]
    self            = "false"
    to_port         = "1234"
  }
}
