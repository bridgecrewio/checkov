# pass
resource "tencentcloud_clb_listener" "positive" {
  clb_id        = "lb-0lh5au7v"
  listener_name = "test_listener"
  protocol      = "HTTPS"
  port          = 443
}

# failed
resource "tencentcloud_clb_listener" "negative1" {
  clb_id        = "lb-0lh5au7v"
  listener_name = "test_listener"
  protocol      = "HTTP"
  port          = 80
}

resource "tencentcloud_clb_listener" "negative2" {
  clb_id        = "lb-0lh5au7v"
  listener_name = "test_listener"
  protocol      = "TCP"
  port          = 8080
}

resource "tencentcloud_clb_listener" "negative3" {
  clb_id        = "lb-0lh5au7v"
  listener_name = "test_listener"
  protocol      = "UDP"
  port          = 8090
}

