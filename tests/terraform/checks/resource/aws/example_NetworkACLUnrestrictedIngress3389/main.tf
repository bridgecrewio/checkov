resource "aws_network_acl_rule" "fail2" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 5
  to_port        = 4000
}

resource "aws_network_acl" "fail" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "10.0.0.0/32"
    from_port  = 22
    to_port    = 22
  }
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "3389"
    to_port    = "3389"
  }


  tags = {
    Name = "main"
    test = "fail"
  }
}

resource "aws_network_acl" "fail2" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 22
    to_port    = 22
  }
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 3389
    to_port    = 3389
  }

  tags = {
    Name = "main"
    test = "fail"
  }
}

resource "aws_network_acl" "pass" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  ingress = [{
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "10.0.0.0/32"
    from_port  = 22
    to_port    = 22
    },
    {
      protocol   = "tcp"
      rule_no    = 110
      action     = "allow"
      cidr_block = "10.0.0.0/32"
      from_port  = 3389
      to_port    = 3389
  }]


  tags = {
    Name = "main"
    test = "fail"
  }
}


resource "aws_network_acl" "pass2" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "deny"
    cidr_block = "0.0.0.0/0"
    from_port  = 22
    to_port    = 22
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "deny"
    cidr_block = "0.0.0.0/0"
    from_port  = 3389
    to_port    = 3389
  }

  tags = {
    Name = "main"
    test = "fail"
  }
}


resource "aws_network_acl" "unknown" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  tags = {
    Name = "main"
    test = "fail"
  }
}

resource "aws_network_acl" "fail3" {
  vpc_id = aws_vpc.main.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 22
    to_port    = 22
  }
  ingress {
    protocol        = "tcp"
    rule_no         = 110
    action          = "allow"
    ipv6_cidr_block = "::/0"
    from_port       = 3389
    to_port         = 3389
  }

  tags = {
    Name = "main"
    test = "fail"
  }
}

resource "aws_network_acl_rule" "fail" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 3389
  to_port        = 3389
}


resource "aws_network_acl_rule" "pass" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "10.0.0.0/32"
  from_port      = 3389
  to_port        = 3389
}

resource "aws_network_acl_rule" "pass2" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "10.0.0.0/32"
  from_port      = 5
  to_port        = 4000
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

provider "aws" {
  region = "eu-west-2"
}

# open all
resource "aws_network_acl_rule" "public_ingress" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 100
  egress         = false
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}


resource "aws_network_acl_rule" "count_pass" {
  count          = length(var.public_nacl_inbound_tcp_ports)
  network_acl_id = "test_id"
  rule_number    = count.index + 101
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = var.public_nacl_inbound_tcp_ports[count.index]
  to_port        = var.public_nacl_inbound_tcp_ports[count.index]
}