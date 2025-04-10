resource "aws_security_group" "pass" {
  name   = "example"
  vpc_id = "aws_vpc.example.id"

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
  }
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 20
    to_port     = 200
    protocol    = "-1"
  }
}

resource "aws_security_group" "fail2" {
  name   = "example"
  vpc_id = "aws_vpc.example.id"

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
  }
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
  }
}

resource "aws_security_group_rule" "pass" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = "sg-12345"
  type              = "egress"
}

resource "aws_vpc_security_group_egress_rule" "pass" {
  security_group_id = aws_security_group.example.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 80
}

# fail
resource "aws_security_group" "fail" {
  name        = "allow-all-ingress"
  description = "unfettered access"
  vpc_id      = "test_vpc"

  egress {
    from_port   = -1
    to_port     = -1
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Test unfettered access"
  }
}


resource "aws_security_group_rule" "fail" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = -1
  to_port           = -1
  protocol          = "tcp"
  security_group_id = "sg-12345"
  description = "Test unfettered access"
  type              = "egress"
}

resource "aws_security_group_rule" "fail2" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = "sg-123456"
  description = "Test unfettered access"
  type              = "egress"
}

resource "aws_vpc_security_group_egress_rule" "fail" {
  security_group_id = aws_security_group.example.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = -1
  ip_protocol = "tcp"
  to_port     = -1
}