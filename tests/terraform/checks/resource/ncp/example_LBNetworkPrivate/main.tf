resource "ncloud_lb" "pass" {
  name = "tf-lb-test"
  network_type = "PRIVATE"
  type = "APPLICATION"
  subnet_no_list = [ ncloud_subnet.test.subnet_no ]
}

resource "ncloud_lb" "fail" {
  name = "tf-lb-test"
  network_type = "PUBLIC"
  type = "APPLICATION"
  subnet_no_list = [ ncloud_subnet.test.subnet_no ]
}
resource "ncloud_lb" "fail2" {
  name = "tf-lb-test"
  type = "APPLICATION"
  subnet_no_list = [ ncloud_subnet.test.subnet_no ]
}