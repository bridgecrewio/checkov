resource "ncloud_subnet" "subnet" {
  vpc_no         = ncloud_vpc.vpc.id
  subnet         = "10.0.1.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc.default_network_acl_no
  subnet_type    = "PUBLIC"
  name           = "subnet-01"
  usage_type     = "GEN"
}

resource "ncloud_route_table" "route_table" {
  vpc_no                = ncloud_vpc.vpc.id
  supported_subnet_type = "PUBLIC"
  name                  = "route-table"
  description           = "for test"
}

resource "ncloud_route_table_association" "pass" {
  route_table_no = ncloud_route_table.route_table.id
  subnet_no      = ncloud_subnet.subnet.id
}

resource "ncloud_subnet" "subnet2" {
  vpc_no         = ncloud_vpc.vpc.id
  subnet         = "10.0.1.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc.default_network_acl_no
  subnet_type    = "PUBLIC"
  name           = "subnet-01"
  usage_type     = "GEN"
}

resource "ncloud_route_table" "route_table2" {
  vpc_no                = ncloud_vpc.vpc.id
  supported_subnet_type = "PRIVATE"
  name                  = "route-table"
  description           = "for test"
}

resource "ncloud_route_table_association" "fail" {
  route_table_no = ncloud_route_table.route_table2.id
  subnet_no      = ncloud_subnet.subnet2.id
}