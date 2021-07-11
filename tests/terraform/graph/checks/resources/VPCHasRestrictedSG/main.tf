resource "aws_vpc" "not_ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "not_ok_vpc_2" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "not_ok_vpc_3" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.ok_vpc.id
}

resource "aws_default_security_group" "default_2" {
  vpc_id = aws_vpc.not_ok_vpc_2.id

  ingress {
    protocol  = "-1"
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_default_security_group" "default_3" {
  vpc_id = aws_vpc.not_ok_vpc_3.id
}

resource "aws_security_group_rule" "default_sg_rule" {
  from_port         = 0
  protocol          = "-1"
  to_port           = 0
  type              = "-1"
  security_group_id = aws_default_security_group.default_3.id
}
