resource "ncloud_server" "server" {
  subnet_no                 = ncloud_subnet.test.id
  name                      = "my-tf-server"
  server_image_product_code = "SW.VSVR.OS.LNX64.CNTOS.0703.B050"
  server_product_code       = "SVR.VSVR.HICPU.C002.M004.NET.SSD.B050.G002"
  login_key_name            = ncloud_login_key.loginkey.key_name
}

resource "ncloud_public_ip" "pass" {
}

resource "ncloud_public_ip" "fail" {
  server_instance_no = ncloud_server.server.instance_no
}

resource "ncloud_public_ip" "fail2" {
  server_instance_no = "551212"
}