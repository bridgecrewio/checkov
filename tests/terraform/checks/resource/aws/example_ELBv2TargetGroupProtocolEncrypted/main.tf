# PASS: protocol is HTTPS
resource "aws_lb_target_group" "pass_https" {
  name     = "tg-pass-https"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTPS"
    path     = "/health"
  }
}

# PASS: protocol is TLS
resource "aws_lb_target_group" "pass_tls" {
  name     = "tg-pass-tls"
  port     = 443
  protocol = "TLS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTPS"
    path     = "/health"
  }
}

# PASS: target_type is lambda (no transport protocol)
resource "aws_lb_target_group" "pass_lambda" {
  name        = "tg-pass-lambda"
  target_type = "lambda"
}

# PASS: alb_target_group with HTTPS
resource "aws_alb_target_group" "pass_alb_https" {
  name     = "tg-pass-alb-https"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = "vpc-123456"

  health_check {
    protocol = "HTTPS"
    path     = "/health"
  }
}

# FAIL: protocol is HTTP
resource "aws_lb_target_group" "fail_http" {
  name     = "tg-fail-http"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "vpc-123456"
}

# FAIL: protocol is TCP (unencrypted)
resource "aws_lb_target_group" "fail_tcp" {
  name     = "tg-fail-tcp"
  port     = 80
  protocol = "TCP"
  vpc_id   = "vpc-123456"
}

# FAIL: protocol is UDP (unencrypted)
resource "aws_lb_target_group" "fail_udp" {
  name     = "tg-fail-udp"
  port     = 53
  protocol = "UDP"
  vpc_id   = "vpc-123456"
}

# FAIL: no protocol specified (defaults to HTTP)
resource "aws_lb_target_group" "fail_no_protocol" {
  name   = "tg-fail-no-protocol"
  port   = 80
  vpc_id = "vpc-123456"
}
