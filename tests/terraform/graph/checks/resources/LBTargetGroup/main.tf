resource "aws_lb_target_group" "fail" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group" "pass" {
  name        = "tf-example-lb-alb-tg"
  target_type = "alb"
  port        = 80
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
}

resource "aws_alb_target_group" "fail" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_alb_target_group" "pass" {
  name     = "tf-example-lb-nlb-tg"
  port     = 25
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id

  target_health_state {
    enable_unhealthy_connection_termination = false
  }
}

resource "aws_lb_listener" "public_load_balancer_https_listener" {
  load_balancer_arn = aws_lb.public_application_load_balancer.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = data.aws_acm_certificate.default_cert.arn

  default_action {
    target_group_arn = aws_lb_target_group.public_fargate_target_group.arn
    type             = "forward"
  }

  depends_on = [aws_lb_target_group.public_fargate_target_group]

  tags = {
    environment        = var.environment
    service_name       = var.service_name
    application_family = var.application_family
    terraformed        = true
  }
}

resource "aws_lb_target_group" "public_fargate_target_group" {
  name                 = "${var.environment}-${var.service_name}-public"
  port                 = "8080"
  protocol             = "HTTP"
  target_type          = "ip"
  deregistration_delay = "60"
  vpc_id               = data.aws_vpc.vpc.id

  health_check {
    enabled             = true
    healthy_threshold   = "3"
    interval            = "10"
    matcher             = "200"
    path                = "/hello/"
    port                = "8080"
    protocol            = "HTTP"
    timeout             = "5"
    unhealthy_threshold = "3"
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = "86400"
    enabled         = false
  }

  tags = {
    environment        = var.environment
    service_name       = var.service_name
    application_family = var.application_family
    terraformed        = true
  }

  depends_on = [aws_lb.public_application_load_balancer]
}

resource "aws_alb_listener" "public_load_balancer_https_listener" {
  load_balancer_arn = aws_lb.public_application_load_balancer.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = data.aws_acm_certificate.default_cert.arn

  default_action {
    target_group_arn = aws_alb_target_group.public_fargate_target_group.arn
    type             = "forward"
  }

  depends_on = [aws_alb_target_group.public_fargate_target_group]

  tags = {
    environment        = var.environment
    service_name       = var.service_name
    application_family = var.application_family
    terraformed        = true
  }
}

resource "aws_alb_target_group" "public_fargate_target_group" {
  name                 = "${var.environment}-${var.service_name}-public"
  port                 = "8080"
  protocol             = "HTTP"
  target_type          = "ip"
  deregistration_delay = "60"
  vpc_id               = data.aws_vpc.vpc.id

  health_check {
    enabled             = true
    healthy_threshold   = "3"
    interval            = "10"
    matcher             = "200"
    path                = "/hello/"
    port                = "8080"
    protocol            = "HTTP"
    timeout             = "5"
    unhealthy_threshold = "3"
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = "86400"
    enabled         = false
  }

  tags = {
    environment        = var.environment
    service_name       = var.service_name
    application_family = var.application_family
    terraformed        = true
  }

  depends_on = [aws_alb.public_application_load_balancer]
}
