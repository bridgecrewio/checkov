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
    from_port       = "22"
    to_port         = "22"
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
    security_groups = ["sg-id-0"]
    self            = "false"
  }

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description     = "Access to Bastion Host Security Group"
    from_port       = "443"
    to_port         = "443"
    protocol        = "tcp"
    security_groups = ["sg-id-0"]
    self            = "false"
    cidr_blocks     = ["0.0.0.0/0", "8.0.4.19/92"]
  }
}

resource "aws_security_group" "sg2" {
  description = "sg2"

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0"]
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
    to_port         = "1234"
  }

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0", "8.0.4.19/92"]
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
    to_port         = "5432"
  }
}

resource "aws_security_group" "sg3" {
  description = "sg2"

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description     = "Access to Bastion Host Security Group"
    from_port       = "22"
    protocol        = "tcp"
    security_groups = ["sg-id-0"]
    cidr_blocks     = ["0.0.0.0/16"]
    self            = "false"
    to_port         = "22"
  }

  egress {
    description = "Self Reference"
    cidr_blocks = ["0.0.0.0/0", "8.0.4.19/92"]
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
    to_port         = "5432"
  }
}
