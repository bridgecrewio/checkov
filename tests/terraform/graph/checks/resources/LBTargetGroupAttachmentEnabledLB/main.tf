provider "ncloud" {
  support_vpc = true
  access_key = var.access_key
  secret_key = var.secret_key
  region = var.region
}

resource "ncloud_launch_configuration" "lc" {
  name = "my-lc"
  server_image_product_code = "SW.VSVR.OS.LNX64.CNTOS.0703.B050"
  server_product_code = "SVR.VSVR.HICPU.C002.M004.NET.SSD.B050.G002"
}

resource "ncloud_vpc" "example" {
  ipv4_cidr_block    = "10.0.0.0/16"
}

resource "ncloud_subnet" "example" {
  vpc_no             = ncloud_vpc.example.vpc_no
  subnet             = "10.0.0.0/24"
  zone               = "KR-2"
  network_acl_no     = ncloud_vpc.example.default_network_acl_no
  subnet_type        = "PRIVATE"
  usage_type         = "LOADB"
}

resource "ncloud_lb" "test" {
  name = "tf-lb-test"
  network_type = "PUBLIC"
  type = "APPLICATION"
  subnet_no_list = [ ncloud_subnet.example.subnet_no ]
}

resource "ncloud_lb_listener" "test" {
  load_balancer_no = ncloud_lb.test.load_balancer_no
  protocol = "HTTP"
  port = 80
  target_group_no = ncloud_lb_target_group.test.target_group_no
}
resource "ncloud_lb_target_group" "test" {
  vpc_no   = ncloud_vpc.example.vpc_no
  protocol = "HTTP"
  target_type = "VSVR"
  port        = 8080
  description = "for test"
  health_check {
    protocol = "HTTP"
    http_method = "GET"
    port           = 8080
    url_path       = "/monitor/l7check"
    cycle          = 30
    up_threshold   = 2
    down_threshold = 2
  }
  algorithm_type = "RR"
}
resource "ncloud_lb_target_group" "test2" {
  vpc_no   = ncloud_vpc.example.vpc_no
  protocol = "HTTP"
  target_type = "VSVR"
  port        = 8080
  description = "for test"
  algorithm_type = "RR"
}

resource "ncloud_auto_scaling_group" "auto" {
  access_control_group_no_list = [ncloud_vpc.example.default_access_control_group_no]
  subnet_no = ncloud_subnet.example.subnet_no
  launch_configuration_no = ncloud_launch_configuration.lc.launch_configuration_no
  desired_capacity = 0
  min_size = 0
  max_size = 5
  health_check_type_code = "LOADB"
  health_check_grace_period = 300
}

resource "ncloud_lb_target_group_attachment" "pass" {
  target_group_no = ncloud_lb_target_group.test.target_group_no
  target_no_list = ncloud_auto_scaling_group.auto.server_instance_no_list
}

resource "ncloud_lb_target_group_attachment" "fail" {
  target_group_no = ncloud_lb_target_group.test2.target_group_no
  target_no_list = ncloud_auto_scaling_group.auto.server_instance_no_list
}






