resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block                            = "0.0.0.0/0"
    vpc_peering_connection_id = var.vpc_peering_connection_id2
  }
  route {
    cidr_block                            = "10.0.0.0/32"
    vpc_peering_connection_id = var.vpc_peering_connection_id1
  }

}