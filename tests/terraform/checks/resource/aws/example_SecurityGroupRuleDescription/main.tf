
resource "aws_security_group" "fail" {
  egress {
    description = "Allow outgoing communication"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }
  egress {
    cidr_blocks = ["10.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }
  ingress {
    description = "Self Reference"
    from_port   = "0"
    protocol    = "-1"
    self        = "true"
    to_port     = "0"
  }

  name = "example-lambda"

  tags = {
    Name = "example-sg"
  }

  vpc_id = aws_vpc.vpc.id
}

resource "aws_security_group" "pass" {
description = "sg_desc"
  egress {
    description = "Allow outgoing communication"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }
  egress {
    description = "Egress description"
    cidr_blocks = ["10.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description = "Self Reference"
    from_port   = "0"
    protocol    = "-1"
    self        = "true"
    to_port     = "0"
  }

  name = "example-lambda"

  tags = {
    Name = "example-sg"
  }

  vpc_id = aws_vpc.vpc.id
}

resource "aws_security_group" "pass2" {
  description = "SG description"
  egress {
    description = "Allow outgoing communication"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    description = "Self Reference"
    from_port   = "0"
    protocol    = "-1"
    self        = "true"
    to_port     = "0"
  }

  name = "example-lambda"

  tags = {
    Name = "example-sg"
  }

  vpc_id = aws_vpc.vpc.id
}

resource "aws_security_group_rule" "fail" {
  type = "ingress"
  from_port = 3389
  to_port = 3389
  protocol = "tcp"
  cidr_blocks = "0.0.0.0/0"
  security_group_id = "sg-123456"
}

resource "aws_security_group_rule" "pass" {
  type = "ingress"
  description = "SG rule description"
  from_port = 3389
  to_port = 3389
  protocol = "tcp"
  cidr_blocks = "0.0.0.0/0"
  security_group_id = "sg-123456"
}

resource "aws_vpc_security_group_ingress_rule" "fail" {
  security_group_id = aws_security_group.example.id

  cidr_ipv4   = "10.0.0.0/8"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 8080
}

resource "aws_vpc_security_group_ingress_rule" "pass" {
  security_group_id = aws_security_group.example.id
  description = "The good stuff"
  cidr_ipv4   = "10.0.0.0/8"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 8080
}
