resource "ncloud_lb_listener" "pass" {
    load_balancer_no = ncloud_lb.lb.id
    protocol = "HTTPS"
    tls_min_version_type = "TLSV12"
    port = 80
    target_group_no = ncloud_lb_target_group.tg.id
}
resource "ncloud_lb_listener" "fail" {
    load_balancer_no = ncloud_lb.lb.id
    protocol = "TLS"
    tls_min_version_type = "TLSV10"
    port = 80
    target_group_no = ncloud_lb_target_group.tg.id
}
resource "ncloud_lb_listener" "fail2" {
    load_balancer_no = ncloud_lb.lb.id
    protocol = "HTTPS"
    port = 80
    target_group_no = ncloud_lb_target_group.tg.id
}