resource "ncloud_lb_target_group" "pass" {
  vpc_no   = ncloud_vpc.test.vpc_no
  protocol = "HTTPS"
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
resource "ncloud_lb_target_group" "fail" {
  vpc_no   = ncloud_vpc.test.vpc_no
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