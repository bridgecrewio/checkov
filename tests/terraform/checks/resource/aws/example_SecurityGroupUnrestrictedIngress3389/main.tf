# pass

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
  type              = "ingress"
}

# fail

resource "aws_security_group" "fail" {
  name   = "example"
  vpc_id = "aws_vpc.example.id"

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 3389
    to_port     = 3389
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

resource "aws_security_group_rule" "fail" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 3389
  to_port           = 3389
  protocol          = "tcp"
  security_group_id = "sg-12345"
  type              = "ingress"
}
