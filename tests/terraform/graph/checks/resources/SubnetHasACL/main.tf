resource "aws_vpc" "ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_network_acl" "acl_ok_optionA" {
  vpc_id = aws_vpc.ok_vpc.id
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.ok_vpc.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "main_optionB" {
  cidr_block = "10.0.1.0/24"
}

resource "aws_network_acl" "acl_ok_optionB" {
  vpc_id = aws_vpc.ok_vpc.id
  subnet_ids = [aws_subnet.main_optionB.id]
}


resource "aws_vpc" "bad_vpc" {
  cidr_block = "10.0.0.0/16"
}


resource "aws_network_acl" "acl_bad_A" {
  vpc_id = aws_vpc.bad_vpc.id
}

resource "aws_network_acl" "acl_bad_B" {
  
}

resource "aws_vpc" "no_nacl_vpc" {
  cidr_block = "10.0.0.0/16"
}

