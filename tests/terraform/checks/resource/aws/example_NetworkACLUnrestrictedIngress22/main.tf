resource "aws_network_acl" "pass3" {
  vpc_id     = aws_vpc.VPC.id
  subnet_ids = aws_subnet.PublicSubnet.*.id

  ingress {
    rule_no    = 10
    protocol   = "tcp"
    action     = "deny"
    cidr_block = "0.0.0.0/0"

    from_port = 20
    to_port   = 22
  }

  ingress {
    rule_no    = 20
    protocol   = "tcp"
    action     = "deny"
    cidr_block = "0.0.0.0/0"

    from_port = 3389
    to_port   = 3389
  }

  ingress {
    rule_no    = 100
    protocol   = -1
    action     = "allow"
    cidr_block = "0.0.0.0/0"

    from_port = 0
    to_port   = 0
  }

  egress {
    rule_no    = 100
    protocol   = -1
    action     = "allow"
    cidr_block = "0.0.0.0/0"

    from_port = 0
    to_port   = 0
  }

  tags = {
    Name = "${var.TagName}-Public"
  }
}

resource "aws_network_acl" "fail4" {
  vpc_id     = aws_vpc.VPC.id
  subnet_ids = aws_subnet.PublicSubnet.*.id

  ingress {
    rule_no    = 30
    protocol   = "tcp"
    action     = "deny"
    cidr_block = "0.0.0.0/0"

    from_port = 20
    to_port   = 22
  }

  ingress {
    rule_no    = 20
    protocol   = "tcp"
    action     = "deny"
    cidr_block = "0.0.0.0/0"

    from_port = 3389
    to_port   = 3389
  }

  ingress {
    rule_no    = 10
    protocol   = -1
    action     = "allow"
    cidr_block = "0.0.0.0/0"

    from_port = 0
    to_port   = 0
  }

  egress {
    rule_no    = 100
    protocol   = -1
    action     = "allow"
    cidr_block = "0.0.0.0/0"

    from_port = 0
    to_port   = 0
  }

  tags = {
    Name = "${var.TagName}-Public"
  }
}

resource "aws_network_acl_rule" "fail2" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 5
  to_port        = 25
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
    cidr_block = "0.0.0.0/0"
    from_port  = 22
    to_port    = 22
  }
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "10.0.0.0/32"
    from_port  = 3389
    to_port    = 3389
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
    cidr_block = "10.0.0.0/32"
    from_port  = 3389
    to_port    = 3389
  }

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
    action     = "allow"
    cidr_block = "10.0.0.0/32"
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
    protocol        = "tcp"
    rule_no         = 100
    action          = "allow"
    ipv6_cidr_block = "::/0"
    from_port       = 22
    to_port         = 22
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


resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

provider "aws" {
  region = "eu-west-2"
}


resource "aws_network_acl_rule" "fail" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 22
  to_port        = 22
}


resource "aws_network_acl_rule" "pass" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "10.0.0.0/32"
  from_port      = 22
  to_port        = 22
}

resource "aws_network_acl_rule" "pass2" {
  network_acl_id = aws_network_acl.pass.id
  rule_number    = 200
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "10.0.0.0/32"
  from_port      = 5
  to_port        = 25
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


resource "aws_network_acl_rule" "pass3" {
  vpc_id = aws_network_acl.pass.id

  egress {
    rule_no    = 200
    action     = "allow"
    cidr_block = "10.3.0.0/18"
    from_port  = false
    to_port    = false
  }

  ingress {
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = false
    to_port    = false
  }
  ingress {
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = false
    to_port    = false
  }


  tags = {
    Name = "main"
    test = "fail"
  }
}

resource "aws_network_acl_rule" "unknown2" {
  vpc_id = aws_network_acl.pass.id
  rule_number    = 100
  ingress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 80
  to_port        = 80
}

resource "aws_network_acl" "mixed_rule_no_types" {
  vpc_id = aws_vpc.main.id

  ingress {
    protocol   = "-1"
    rule_no    = "800" # string
    action     = "deny"
    cidr_block = "10.0.0.0/8"
    from_port  = 0
    to_port    = 0
  }

  ingress {
    protocol   = "-1"
    rule_no    = 900 # int
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }
}

resource "aws_network_acl" "dynamic_rule_no" {
  vpc_id = aws_vpc.main.id

  ingress {
    protocol   = "tcp"
    rule_no    = 204
    action     = "allow"
    cidr_block = "10.0.5.0/24"
    from_port  = 22
    to_port    = 22
  }

  dynamic "ingress" {
    for_each = { for idx, cidr in var.peered_cidr_blocks : idx => cidr }
    content {
      protocol   = "tcp"
      rule_no    = 220 + tonumber(ingress.key)
      action     = "allow"
      cidr_block = ingress.value
      from_port  = 22
      to_port    = 22
    }
  }

  ingress {
    protocol   = "-1"
    rule_no    = 213
    action     = "deny"
    cidr_block = "10.0.0.0/16"
    from_port  = 0
    to_port    = 0
  }
}
