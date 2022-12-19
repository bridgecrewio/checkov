
resource "ncloud_access_control_group" "pass" {
  name        = "my-acg"
  description = "description"
  vpc_no      = ncloud_vpc.vpc.id
}

resource "ncloud_access_control_group_rule" "acg-rule" {
  access_control_group_no = ncloud_access_control_group.pass.id
}

resource "ncloud_access_control_group" "fail" {
  name        = "my-acg"
  description = "description"
  vpc_no      = ncloud_vpc.vpc.id
}