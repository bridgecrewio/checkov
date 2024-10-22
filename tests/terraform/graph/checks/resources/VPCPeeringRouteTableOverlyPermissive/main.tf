resource "aws_route" "aws_route_pass_1" {
  route_table_id            = "rtb-4fbb3ac4"
  destination_cidr_block    = "10.0.1.0/22"
  vpc_peering_connection_id = "pcx-45ff3dc1"
}

resource "aws_route" "aws_route_pass_2" {
  route_table_id            = "rtb-4fbb3ac4"
  destination_ipv6_cidr_block = "2002::1234:abcd:ffff:c0a8:101/64"
  vpc_peering_connection_id = "pcx-45ff3dc1"
}

resource "aws_route" "aws_route_pass_3" {
  route_table_id            = "rtb-4fbb3ac4"
  destination_ipv6_cidr_block = "2002::1234:abcd:ffff:c0a8:101/64"
  instance_id = aws_instance.example.id
}

resource "aws_route" "aws_route_fail_1" {
  route_table_id            = "rtb-4fbb3ac4"
  destination_cidr_block    = "0.0.0.0/0"
  vpc_peering_connection_id = "pcx-45ff3dc1"
}

resource "aws_route" "aws_route_fail_2" {
  route_table_id            = "rtb-4fbb3ac4"
  destination_ipv6_cidr_block = "::/0"
  vpc_peering_connection_id = "pcx-45ff3dc1"
}

resource "aws_route_table" "aws_route_table_pass_1" {
  vpc_id = aws_vpc.example.id

  route {
    ipv6_cidr_block = "::/0"
    gateway_id = aws_internet_gateway.example.id
    instance_id = aws_instance.example.id
  }
}

resource "aws_route_table" "aws_route_table_pass_2" {
  vpc_id = aws_vpc.example.id

  route {
    ipv6_cidr_block = "2002::1234:abcd:ffff:c0a8:101/64"
    vpc_peering_connection_id = "pcx-45ff3dc1"
  }
}

resource "aws_route_table" "aws_route_table_pass_3" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "10.0.1.0/22"
    vpc_peering_connection_id = "pcx-45ff3dc1"
  }
}

resource "aws_route_table" "aws_route_table_fail_1" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "0.0.0.0/0"
    vpc_peering_connection_id = "pcx-45ff3dc1"
  }
}

resource "aws_route_table" "aws_route_table_fail_2" {
  vpc_id = aws_vpc.example.id

  route {
    ipv6_cidr_block = "::/0"
    vpc_peering_connection_id = "pcx-45ff3dc1"
  }
}

resource "aws_route" "aws_route_pass_4" {
  route_table_id            = aws_route_table.rtb1.id
  destination_cidr_block    = "10.1.0.0/16"
  vpc_peering_connection_id = "pcx-578451154151544"
}

resource "aws_route" "aws_route_pass_5" {
  route_table_id            = aws_route_table.rtb2.id
  destination_cidr_block    = "10.0.0.0/16"
  vpc_peering_connection_id = "pcx-578451154151544"
}