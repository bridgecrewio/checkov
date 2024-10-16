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