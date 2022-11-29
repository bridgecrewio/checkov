resource "ncloud_lb_listener" "pass" {
  load_balancer_no = ncloud_lb.test.load_balancer_no
  protocol = "HTTPS"
  port = 80
  target_group_no = ncloud_lb_target_group.test.target_group_no
}
resource "ncloud_lb_listener" "fail" {
  load_balancer_no = ncloud_lb.test.load_balancer_no
  protocol = "HTTP"
  port = 80
  target_group_no = ncloud_lb_target_group.test.target_group_no
}