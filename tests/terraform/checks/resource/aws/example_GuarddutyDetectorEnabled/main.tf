resource "aws_guardduty_detector" "pass" {
  enable = true
  tags   = { test = "Fail" }
}

resource "aws_guardduty_detector" "pass2" {
  tags = { test = "Fail" }
}

resource "aws_guardduty_detector" "fail" {
  enable = false
  tags   = { test = "Fail" }
}