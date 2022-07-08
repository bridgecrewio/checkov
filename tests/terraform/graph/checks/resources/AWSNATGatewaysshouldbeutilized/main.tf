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

/*
  In the tf plan files the instance id can be included but blank
  "address": "aws_route_table.example",
    "mode": "managed",
    "type": "aws_route_table",
    "name": "example",
    "provider_name": "registry.terraform.io/hashicorp/aws",
    "schema_version": 0,
    "values": {
      "route": [
        {
          "carrier_gateway_id": "",
          "cidr_block": "0.0.0.0/0",
          "destination_prefix_list_id": "",
          "egress_only_gateway_id": "",
          "gateway_id": "",
  --->    "instance_id": "",
          "ipv6_cidr_block": "",
          "local_gateway_id": "",
          "network_interface_id": "",
          "transit_gateway_id": "",
          "vpc_endpoint_id": "",
          "vpc_peering_connection_id": ""
        }
      ],
*/
resource "aws_route" "aws_route_ok_blank_instance" {
  route_table_id            = aws_route_table.example.id
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id                = aws_internet_gateway.example.id
  instance_id               = ""
}

resource "aws_route" "aws_route_not_ok" {
  route_table_id            = aws_route_table.example.id
  destination_cidr_block    = "0.0.0.0/0"
  instance_id               = aws_instance.example.id
}