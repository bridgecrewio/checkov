resource "ncloud_access_control_group_rule" "pass" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "10.3.0.0/18"
        port_range = "22"
        description = "inbound 22"
    }
    outbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "1-65535"
        description = "accept 1-65535 port"
    }
}


resource "ncloud_access_control_group_rule" "pass2" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "20"
        description = "inbound 20"
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


resource "ncloud_access_control_group_rule" "fail2" {
    access_control_group_no = ncloud_access_control_group.acg.id

    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "80"
        description = "inbound 80"
    }
    inbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "22"
        description = "inbound 22"
    }
    outbound {
        protocol = "TCP"
        ip_block = "0.0.0.0/0"
        port_range = "1-65535"
        description = "accept 1-65535 port"
    }
}
