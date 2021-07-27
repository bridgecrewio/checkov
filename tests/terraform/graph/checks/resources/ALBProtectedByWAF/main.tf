resource "aws_lb" "lb_good_1" {
  internal= false
}

resource "aws_lb" "lb_good_2" {
}

resource "aws_wafregional_web_acl_association" "foo" {
  resource_arn = aws_alb.lb_good_1.arn
  web_acl_id = aws_wafregional_web_acl.foo.id
}

resource "aws_wafregional_web_acl_association" "bar" {
  resource_arn = aws_alb.lb_good_2.arn
  web_acl_id = aws_wafregional_web_acl.foo.id
}

resource "aws_lb" "lb_bad_1" {
  internal=true
}



