resource "aws_guardduty_detector" "pass" {
  enable = true
  finding_publishing_frequency = "FIFTEEN_MINUTES"
}

resource "aws_guardduty_detector" "pass2" {
  enable = true
  finding_publishing_frequency = "ONE_HOUR"
}
