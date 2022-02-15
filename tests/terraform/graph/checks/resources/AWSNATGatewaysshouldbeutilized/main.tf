resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id
}

resource "aws_instance" "example" {
  ami           = "ami-005e54dee72cc1d00"
  instance_type = "t2.micro"
  associate_public_ip_address = true
}

resource "aws_route_table" "example" {
  vpc_id = aws_vpc.example.id
}

resource "aws_route_table" "aws_route_table_ok_1" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.example.id
  }
}

resource "aws_route_table" "aws_route_table_ok_2" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "10.0.0.0/24"
    instance_id = aws_instance.example.id
  }
}

resource "aws_route_table" "aws_route_table_not_ok" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "0.0.0.0/0"
    instance_id = aws_instance.example.id
  }
}

resource "aws_route" "aws_route_ok_1" {
  route_table_id            = aws_route_table.example.id
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id                = aws_internet_gateway.example.id
}

resource "aws_route" "aws_route_ok_2" {
  route_table_id            = aws_route_table.example.id
  destination_cidr_block    = "10.0.0.0/24"
  instance_id               = aws_instance.example.id
}

resource "aws_route" "aws_route_not_ok" {
  route_table_id            = aws_route_table.example.id
  destination_cidr_block    = "0.0.0.0/0"
  instance_id               = aws_instance.example.id
}