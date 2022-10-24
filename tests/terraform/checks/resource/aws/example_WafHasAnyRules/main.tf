
//global
resource "aws_waf_web_acl" "fail" {
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }
}

resource "aws_waf_web_acl" "fail2" {
  name        = "tfWebACLfail2"
  metric_name = "tfWebACLfail2"

  default_action {
    type = "ALLOW"
  }
  rules {

  }
}

provider "aws" {
  region = "us-east-1"
}

//global
resource "aws_waf_web_acl" "pass" {
  name        = "tfWebACLpass"
  metric_name = "tfWebACLpass"

  default_action {
    type = "ALLOW"
  }

  rules {
    priority = 1
    rule_id  = "30231cc1-ae2d-44e9-8212-dfb6185288a8"
    type     = "REGULAR"

    action {
      type = "BLOCK"
    }
  }
}

resource "aws_wafregional_web_acl" "pass" {
  name        = "tfWebACLregional"
  metric_name = "tfWebACLregional"

  default_action {
    type = "ALLOW"
  }

  rule {
    action {
      type = "BLOCK"
    }

    priority = 1
    rule_id  = aws_wafregional_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_wafregional_web_acl" "fail" {
  name        = "tfWebACLregionalfail"
  metric_name = "tfWebACLregionalfail"

  default_action {
    type = "ALLOW"
  }

}

resource "aws_wafregional_web_acl" "fail2" {
  name        = "tfWebACLregionalfail2"
  metric_name = "tfWebACLregionalfail2"

  default_action {
    type = "ALLOW"
  }

  rule {
  }
}

