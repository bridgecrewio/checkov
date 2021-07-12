resource "aws_eip" "fixed" {
	# checkov:skip=CKV2_AWS_19: ADD REASON
}

resource "aws_route53_record" "pass" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "dns.freebeer.site"
  type    = "A"
  ttl     = "300"
  records = [aws_eip.fixed.public_ip]
}

resource "aws_api_gateway_domain_name" "example" {
  certificate_arn = aws_acm_certificate_validation.example.certificate_arn
  domain_name     = "api.example.com"
}

resource "aws_route53_record" "pass2" {
  name    = aws_api_gateway_domain_name.example.domain_name
  type    = "A"
  zone_id = aws_route53_zone.example.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.example.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.example.cloudfront_zone_id
  }
}



resource "aws_route53_record" "fail" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "dns.freebeer.site"
  type    = "A"
  ttl     = "300"
  records = ["1.1.1.1"]
}

resource "aws_route53_record" "ignore" {
  zone_id = data.aws_route53_zone.parent.id
  name    = "Some name abcd"
  type    = "CNAME"
  ttl     = 60
  records = [module.controller.loadbalancer_dns_name]
}
