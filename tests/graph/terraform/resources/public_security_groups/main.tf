resource "aws_vpc" "my_vpc" {
  cidr_block = "172.16.0.0/16"

  tags = {
    Name = "tf-example"
  }
}

resource "aws_security_group" "aws_security_group_public" {
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 0
    protocol = ""
    to_port = 0
  }
}

resource "aws_security_group" "aws_security_group_private" {
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    cidr_blocks = ["25.09.19.92/0"]
    from_port = 0
    protocol = ""
    to_port = 0
  }
}

resource "aws_db_security_group" "aws_db_security_group_public" {
  name = "rds_sg"

  ingress {
    cidr = "0.0.0.0"
  }
}

resource "aws_db_security_group" "aws_db_security_group_private" {
  name = "rds_sg"

  ingress {
    cidr = "10.0.0.0/24"
  }
}

resource "aws_redshift_security_group" "aws_redshift_security_group_public" {
  name = "redshift-sg"

  ingress {
    cidr = "0.0.0.0"
  }
}

resource "aws_redshift_security_group" "aws_redshift_security_group_private" {
  name = "redshift-sg"

  ingress {
    cidr = "25.09.19.92/0"
  }
}

resource "aws_elasticache_security_group" "aws_elasticache_security_group_public" {
  name                 = "elasticache-security-group"
  security_group_names = [aws_security_group.aws_security_group_public.name]
}

resource "aws_elasticache_security_group" "aws_elasticache_security_group_private" {
  name                 = "elasticache-security-group"
  security_group_names = [aws_security_group.aws_security_group_private.name]
}