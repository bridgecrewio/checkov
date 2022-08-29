#pass
resource "aws_route53_zone" "pass" {
  name = "pass"
}
resource "aws_route53_query_log" "pass" {
  depends_on = [aws_cloudwatch_log_resource_policy.route53-query-logging-policy]
  cloudwatch_log_group_arn = aws_cloudwatch_log_group.aws_route53_pass.arn
  zone_id                  = aws_route53_zone.pass.zone_id
}

#fail
resource "aws_route53_zone" "fail" {
  name = "fail"
}
