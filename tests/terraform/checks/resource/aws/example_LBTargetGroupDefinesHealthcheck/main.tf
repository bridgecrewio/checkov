
resource "aws_lb_target_group" "fail" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check {
    enabled=false  # trigger- defaults to true
  }
}

resource "aws_lb_target_group" "fail2" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group" "fail3" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check = [{}]
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_alb_target_group" "pass" {
  name = "target-group-1"
  port = 80
  protocol = "HTTP"

  health_check {
    path = "/api/1/resolve/default?path=/service/my-service"
    port = 2001
    healthy_threshold = 6
    unhealthy_threshold = 2
    timeout = 2
    interval = 5
    matcher = "200"  # has to be HTTP 200 or fails
  }
}