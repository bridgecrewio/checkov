# pass
resource "tencentcloud_instance" "default" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
}

resource "tencentcloud_instance" "orderly_security_groups_sg" {
  instance_name           = "tf-cvm-basic"
  availability_zone       = "ap-guangzhou-3"
  orderly_security_groups = ["tencentcloud_security_group.sg.id"]
}

resource "tencentcloud_instance" "security_groups_sg" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  security_groups   = ["tencentcloud_security_group.sg.id"]
}

# failed
resource "tencentcloud_instance" "orderly_security_groups_default" {
  instance_name           = "tf-cvm-basic"
  availability_zone       = "ap-guangzhou-3"
  orderly_security_groups = ["tencentcloud_security_group.default.id"]
}

resource "tencentcloud_instance" "security_groups_default" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  security_groups   = ["tencentcloud_security_group.default.id"]
}