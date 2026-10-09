# PASS: health_check protocol is HTTPS
resource "aws_lb_target_group" "pass_https" {
  name     = "tg-pass-https"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTPS"
    path     = "/health"
    port     = "443"
  }
}

# PASS: target_type is lambda (no health check applies)
resource "aws_lb_target_group" "pass_lambda" {
  name        = "tg-pass-lambda"
  target_type = "lambda"
}

# PASS: transport protocol is TCP (cannot use HTTPS health checks)
resource "aws_lb_target_group" "pass_tcp" {
  name     = "tg-pass-tcp"
  port     = 80
  protocol = "TCP"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "TCP"
    port     = "80"
  }
}

# PASS: transport protocol is UDP (cannot use HTTPS health checks)
resource "aws_lb_target_group" "pass_udp" {
  name     = "tg-pass-udp"
  port     = 53
  protocol = "UDP"
  vpc_id   = "vpc-123456"
}

# PASS: transport protocol is TCP_UDP (cannot use HTTPS health checks)
resource "aws_lb_target_group" "pass_tcp_udp" {
  name     = "tg-pass-tcp-udp"
  port     = 80
  protocol = "TCP_UDP"
  vpc_id   = "vpc-123456"
}

# PASS: transport protocol is GENEVE (cannot use HTTPS health checks)
resource "aws_lb_target_group" "pass_geneve" {
  name     = "tg-pass-geneve"
  port     = 6081
  protocol = "GENEVE"
  vpc_id   = "vpc-123456"
}

# PASS: alb_target_group with HTTPS health check
resource "aws_alb_target_group" "pass_alb" {
  name     = "tg-pass-alb"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTPS"
    path     = "/health"
  }
}

# FAIL: health_check protocol is HTTP
resource "aws_lb_target_group" "fail_http_health_check" {
  name     = "tg-fail-http-hc"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTP"
    path     = "/health"
    port     = "80"
  }
}

# FAIL: no health_check block (defaults to HTTP)
resource "aws_lb_target_group" "fail_no_health_check" {
  name     = "tg-fail-no-hc"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"
}

# FAIL: TLS protocol with HTTP health check (NLB TLS targets should still have HTTPS health check)
resource "aws_lb_target_group" "fail_tls_http_health_check" {
  name     = "tg-fail-tls-http-hc"
  port     = 443
  protocol = "TLS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTP"
    path     = "/health"
    port     = "80"
  }
}
