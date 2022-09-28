resource "ncloud_access_control_group" "pass" {
    name = "example-acg"
    vpc_no = data.ncloud_vpc.selected.id
    description = "description"
}

resource "ncloud_access_control_group" "fail" {
    name = "example-acg"
    vpc_no = data.ncloud_vpc.selected.id
}