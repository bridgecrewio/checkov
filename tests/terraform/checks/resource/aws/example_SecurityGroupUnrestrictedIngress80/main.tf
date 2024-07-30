
resource "aws_security_group" "fail" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "fail2" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "fail3" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    ipv6_cidr_blocks = ["192.168.0.0/16", "::/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "fail4" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "fail5" {
  description = "SG with inline rules"
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "Wide Open"
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      protocol         = "-1"
      self             = false
      to_port          = 65535
    }
  ]
}

resource "aws_security_group" "pass" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 222
    to_port   = 222
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass2" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass3" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress = [{
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    description = "foo"
    cidr_blocks = null
  }]

  egress = [{
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = null
  }]
}

resource "aws_security_group" "pass4" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass5" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    cidr_blocks = ["192.168.0.0/16"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass6" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass7" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "pass-ipv6" {
      name   = "sg-bar"
      vpc_id = aws_vpc.main.id

      ingress = [{
        ipv6_cidr_blocks = null
        from_port = 80
        to_port   = 80
        protocol  = "tcp"
        security_groups = [aws_security_group.foo-sg.id]
        description = "foo"
        cidr_blocks = null
      }]

      egress = [{
        from_port = 0
        to_port   = 0
        protocol  = "-1"
        cidr_blocks = null
      }]
    }

resource "aws_security_group_rule" "fail" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["192.168.0.0/16", "0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}

resource "aws_security_group_rule" "pass" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["192.168.0.0/16"]
  security_group_id = aws_security_group.bar-sg.id
}

resource "aws_security_group_rule" "unknown" {
  type              = "egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}

resource "aws_security_group_rule" "pass2" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  source_security_group_id       = "sg-123456"
  security_group_id = aws_security_group.bar-sg.id
}

resource "aws_security_group_rule" "pass3" {
  type              = "ingress"
  from_port         = 222
  to_port           = 222
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}

resource "aws_vpc_security_group_ingress_rule" "fail" {
  security_group_id = aws_security_group.example.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 80
}

resource "aws_vpc_security_group_ingress_rule" "fail2" {
  security_group_id = aws_security_group.example.id
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 80
}

resource "aws_vpc_security_group_ingress_rule" "pass_prefix_list" {
  prefix_list_ids = "some_id"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 80
}

resource "aws_vpc_security_group_ingress_rule" "pass" {
  security_group_id = aws_security_group.example.id

  cidr_ipv4   = "10.0.0.0/8"
  from_port   = 80
  ip_protocol = "tcp"
  to_port     = 80
}