#pass
resource "aws_route53_zone" "pass" {
  name = "pass"
}
resource "aws_route53_key_signing_key" "pass" {
  hosted_zone_id             = aws_route53_zone.pass.id
  key_management_service_arn = aws_kms_key.pass.arn
  name                       = "pass"
}

resource "aws_route53_hosted_zone_dnssec" "pass" {
  depends_on = [
    aws_route53_key_signing_key.pass
  ]
  hosted_zone_id = aws_route53_key_signing_key.pass.hosted_zone_id
}

# private hosted zone with inline VPC configuration block
resource "aws_route53_zone" "private_with_inline_vpc" {
  name = "private"

  vpc {
    vpc_id = "vpc-1a2b3c4d"
  }
}

# private hosted zone with connected aws_route53_zone_association
resource "aws_route53_zone" "private_with_zone_association" {
  name = "private"
}

resource "aws_route53_zone_association" "private" {
  zone_id = aws_route53_zone.private_with_zone_association.zone_id
  vpc_id  = "vpc-1a2b3c4d"
}

#fail
resource "aws_route53_zone" "fail" {
  name = "fail"
}
resource "aws_route53_key_signing_key" "fail" {
  hosted_zone_id             = aws_route53_zone.fail.id
  key_management_service_arn = aws_kms_key.fail.arn
  name                       = "pass"
}

#fail2
resource "aws_route53_zone" "fail2" {
  name = "fail2"
}