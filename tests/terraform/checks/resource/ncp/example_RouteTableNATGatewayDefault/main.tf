resource "ncloud_vpc" "vpc" {
  name            = "vpc"
  ipv4_cidr_block = "10.0.0.0/16"
}

resource "ncloud_route_table" "route_table" {
  vpc_no                = ncloud_vpc.vpc.id
  supported_subnet_type = "PUBLIC"
}

resource "ncloud_nat_gateway" "nat_gateway" {
  vpc_no = ncloud_vpc.vpc.id
  zone   = "KR-2"
}

resource "ncloud_route" "pass" {
  route_table_no         = ncloud_route_table.route_table.id
  destination_cidr_block = "0.0.0.0/0"
  target_type            = "NATGW"  // NATGW (NAT Gateway) | VPCPEERING (VPC Peering) | VGW (Virtual Private Gateway).
  target_name            = ncloud_nat_gateway.nat_gateway.name
  target_no              = ncloud_nat_gateway.nat_gateway.id
}

resource "ncloud_route" "fail" {
  route_table_no         = ncloud_route_table.route_table.id
  destination_cidr_block = "0.0.0.1/0"
  target_type            = "NATGW"  // NATGW (NAT Gateway) | VPCPEERING (VPC Peering) | VGW (Virtual Private Gateway).
  target_name            = ncloud_nat_gateway.nat_gateway.name
  target_no              = ncloud_nat_gateway.nat_gateway.id
}