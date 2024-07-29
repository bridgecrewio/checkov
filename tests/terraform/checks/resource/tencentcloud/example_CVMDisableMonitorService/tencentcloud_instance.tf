# pass
resource "tencentcloud_instance" "default" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
}

resource "tencentcloud_instance" "disabled" {
  instance_name           = "tf-cvm-basic"
  availability_zone       = "ap-guangzhou-3"
  disable_monitor_service = false
}

# failed
resource "tencentcloud_instance" "enabled" {
  instance_name           = "tf-cvm-basic"
  availability_zone       = "ap-guangzhou-3"
  disable_monitor_service = true
}