# pass
resource "tencentcloud_instance" "default" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
}

resource "tencentcloud_instance" "disabled" {
  instance_name      = "tf-cvm-basic"
  availability_zone  = "ap-guangzhou-3"
  allocate_public_ip = false
}

# failed
resource "tencentcloud_instance" "enabled" {
  instance_name      = "tf-cvm-basic"
  availability_zone  = "ap-guangzhou-3"
  allocate_public_ip = true
}