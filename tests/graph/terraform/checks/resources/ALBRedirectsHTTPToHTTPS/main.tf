resource "aws_lb" "lb_good_1" {
}

resource "aws_lb" "lb_good_2" {
}

resource "aws_lb" "lb_bad_1" {
}

resource "aws_lb_listener" "listener_good_1" {
  load_balancer_arn = aws_lb.lb_good_1.arn
  port = "443"
  protocol = "HTTPS"

  default_action {
    type = "action"
  }
}

resource "aws_lb_listener" "listener_good_2" {
  load_balancer_arn = aws_lb.lb_good_2.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }

  }
}

resource "aws_lb_listener" "listener_bad_1" {
  load_balancer_arn = aws_lb.lb_bad_1.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "some-action"
  }
}