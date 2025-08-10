# FAIL
resource "aws_lb_listener" "front_end_failing" {
  load_balancer_arn = aws_lb.example_failing.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08" # This policy includes some weak ciphers
  certificate_arn   = "arn:aws:acm:us-west-2:123456789012:certificate/abcdef-1234-5678-abcd-123456789012"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example.arn
  }
}

resource "aws_alb_listener" "insecure_listener" {
  load_balancer_arn = aws_lb.insecure_lb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2015-05" # Weak policy

  certificate_arn = "arn:aws:acm:region:account:certificate/certificate-id"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Insecure"
      status_code  = "200"
    }
  }
}

resource "aws_lb_listener" "insecure_no_policy" {
  load_balancer_arn = aws_lb.insecure_lb.arn
  port              = "443"
  protocol          = "HTTPS"

  certificate_arn = "arn:aws:acm:region:account:certificate/certificate-id"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Insecure"
      status_code  = "200"
    }
  }
}


# PASS
resource "aws_lb_listener" "front_end_passing" {
  load_balancer_arn = aws_lb.example_passing.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01" # This policy includes only strong ciphers
  certificate_arn   = "arn:aws:acm:us-west-2:123456789012:certificate/abcdef-1234-5678-abcd-123456789012"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example.arn
  }
}

resource "aws_alb_listener" "secure_listener" {
  load_balancer_arn = aws_lb.secure_lb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-Ext-2018-06"

  certificate_arn = "arn:aws:acm:region:account:certificate/certificate-id"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "OK"
      status_code  = "200"
    }
  }
}

resource "aws_alb_listener" "secure_listener2" {
  load_balancer_arn = aws_lb.secure_lb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-Ext2-2021-06"

  certificate_arn = "arn:aws:acm:region:account:certificate/certificate-id"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "OK"
      status_code  = "200"
    }
  }
}

resource "aws_lb_listener" "tcp" {
  load_balancer_arn = aws_lb.external_lb.arn
  port              = 443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.external_tg.arn
  }
}