resource "ncloud_access_control_group" "pass" {
    name = "example-acg"
    vpc_no = data.ncloud_vpc.selected.id
    description = "description"
}


resource "ncloud_access_control_group" "fail" {
    name = "example-acg"
    vpc_no = data.ncloud_vpc.selected.id
}


resource "ncloud_access_control_group_rule" "pass" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "22"
        description = "inbound 22"
    }
    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "80"
        description = "inbound 80"
    }
    outbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "1-65535"
        description = "accept 1-65535 port"
    }
}


resource "ncloud_access_control_group_rule" "fail" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "22"
        description = "inbound 22"
    }
    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "80"
    }
    outbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "1-65535"
    }
}


resource "ncloud_access_control_group_rule" "fail2" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "22"
    }
    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "80"
    }
    outbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "1-65535"
    }
}
