resource "ncloud_vpc" "vpc" {
  ipv4_cidr_block = "10.0.0.0/16"
}

resource "ncloud_vpc" "vpc1" {
  ipv4_cidr_block = "10.1.0.0/16"
}

resource "ncloud_subnet" "subnet1" {
  vpc_no         = ncloud_vpc.vpc.id
  subnet         = "10.0.1.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc.default_network_acl_no
  subnet_type    = "PRIVATE"
  name           = "subnet-10"
  usage_type     = "GEN"
}

resource "ncloud_subnet" "subnet2" {
  vpc_no         = ncloud_vpc.vpc1.id
  subnet         = "10.1.2.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc1.default_network_acl_no
  subnet_type    = "PRIVATE"
  name           = "subnet-11"
  usage_type     = "GEN"
}

resource "ncloud_route_table" "pass" {
  vpc_no                = ncloud_vpc.vpc.id
  supported_subnet_type = "PRIVATE"
}

resource "ncloud_route_table" "pass2" {
  vpc_no                = ncloud_vpc.vpc1.id
  supported_subnet_type = "PRIVATE"
}
####
resource "ncloud_vpc" "vpc2" {
  ipv4_cidr_block = "10.0.0.0/16"
}
resource "ncloud_vpc" "vpc3" {
  ipv4_cidr_block = "10.1.0.0/16"
}

resource "ncloud_subnet" "subnet1" {
  vpc_no         = ncloud_vpc.vpc2.id
  subnet         = "10.0.1.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc2.default_network_acl_no
  subnet_type    = "PUBLIC"
  name           = "subnet-10"
  usage_type     = "GEN"
}

resource "ncloud_subnet" "subnet2" {
  vpc_no         = ncloud_vpc.vpc3.id
  subnet         = "10.1.2.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc2.default_network_acl_no
  subnet_type    = "PRIVATE"
  name           = "subnet-11"
  usage_type     = "GEN"
}

resource "ncloud_route_table" "pass3" {
  vpc_no                = ncloud_vpc.vpc3.id
  supported_subnet_type = "PRIVATE"
}

resource "ncloud_route_table" "fail" {
  vpc_no                = ncloud_vpc.vpc2.id
  supported_subnet_type = "PRIVATE"
}
resource "ncloud_route_table" "fail2" {
  supported_subnet_type = "PRIVATE"
}
###
resource "ncloud_vpc" "vpc4" {
  ipv4_cidr_block = "10.0.0.0/16"
}

resource "ncloud_subnet" "subnet1" {
  vpc_no         = ncloud_vpc.vpc4.id
  subnet         = "10.0.1.0/24"
  zone           = "KR-2"
  network_acl_no = ncloud_vpc.vpc4.default_network_acl_no
  subnet_type    = "PRIVATE"
  name           = "subnet-10"
  usage_type     = "GEN"
}


