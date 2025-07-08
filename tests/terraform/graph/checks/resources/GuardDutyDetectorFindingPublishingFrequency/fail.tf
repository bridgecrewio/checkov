resource "aws_guardduty_detector" "fail" {
  enable = true
  finding_publishing_frequency = "SIX_HOURS"
}

resource "aws_guardduty_detector" "fail2" {
  enable = true
  finding_publishing_frequency = "THREE_HOURS"
}
