resource "openstack_lb_pool_v2" "pass" {
  protocol    = "HTTP"
  lb_method   = "ROUND_ROBIN"
  listener_id = "d9415786-5f1a-428b-b35f-2f1523e146d2"

  persistence {
    type        = "APP_COOKIE"
    cookie_name = "testCookie"
  }
}
resource "openstack_lb_monitor_v2" "monitor_1" {
  pool_id     = "${openstack_lb_pool_v2.pass.id}"
  type        = "PING"
  delay       = 20
  timeout     = 10
  max_retries = 5
}
resource "openstack_lb_pool_v2" "pass2" {
  protocol    = "TCP"
  lb_method   = "ROUND_ROBIN"
  listener_id = "d9415786-5f1a-428b-b35f-2f1523e146d2"

  persistence {
    type        = "APP_COOKIE"
    cookie_name = "testCookie"
  }
}

resource "openstack_lb_pool_v2" "fail" {
  protocol    = "HTTP"
  lb_method   = "ROUND_ROBIN"
  listener_id = "d9415786-5f1a-428b-b35f-2f1523e146d2"

  persistence {
    type        = "APP_COOKIE"
    cookie_name = "testCookie"
  }
}
resource "openstack_lb_pool_v2" "fail2" {
  protocol    = "HTTPS"
  lb_method   = "ROUND_ROBIN"
  listener_id = "d9415786-5f1a-428b-b35f-2f1523e146d2"

  persistence {
    type        = "APP_COOKIE"
    cookie_name = "testCookie"
  }
}