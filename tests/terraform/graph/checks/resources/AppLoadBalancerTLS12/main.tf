# pass

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTP"
  port              = "80"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "tcp" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TCP"
  port              = "8080"

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "udp" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "UDP"
  port              = "8080"

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "tcp_udp" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TCP_UDP"
  port              = "8080"

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "tls_1_3" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TLS"
  port              = "8080"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "tls_fs_1_2" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TLS"
  port              = "8080"
  ssl_policy        = "ELBSecurityPolicy-FS-1-2-Res-2019-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "https_fs_1_2" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTPS"
  port              = "443"
  ssl_policy        = "ELBSecurityPolicy-FS-1-2-Res-2019-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_alb_listener" "https_fs_1_2" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTPS"
  port              = "443"
  ssl_policy        = "ELBSecurityPolicy-FS-1-2-Res-2019-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

# gateway LB
resource "aws_lb" "gateway_lb" {
  load_balancer_type = "gateway"
  name               = "example"
}

resource "aws_lb_listener" "gateway_listener" {
  load_balancer_arn = aws_lb.gateway_lb.id
}


# failure

resource "aws_lb_listener" "http" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTP"
  port              = "80"

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "https_2016" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTPS"
  port              = "443"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_lb_listener" "tls_fs_1_1" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TLS"
  port              = "8080"
  ssl_policy        = "ELBSecurityPolicy-FS-1-1-2019-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

resource "aws_alb_listener" "tls_fs_1_1" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "TLS"
  port              = "8080"
  ssl_policy        = "ELBSecurityPolicy-FS-1-1-2019-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = var.aws_lb_target_group_arn
  }
}

# mimicking a Terraform plan output by using an empty block

resource "aws_lb_listener" "cognito" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTP"
  port              = "80"

  default_action {
    type = "authenticate-cognito"

    redirect {
    }
  }
}

resource "aws_lb_listener" "wrong_redirect" {
  load_balancer_arn = var.aws_lb_arn
  protocol          = "HTTP"
  port              = "80"

  default_action {
    type = "redirect"

    redirect {
      protocol = "HTTP"
    }
  }
}

# not gateway LB
resource "aws_lb" "not_gateway_lb" {
  load_balancer_type = "not gateway"
  name               = "example"
}

resource "aws_lb_listener" "not_gateway_listener" {
  load_balancer_arn = aws_lb.not_gateway_lb.id
}
