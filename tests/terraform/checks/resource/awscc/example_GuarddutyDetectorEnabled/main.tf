resource "awscc_guardduty_detector" "pass" {
  enable = true
}

resource "awscc_guardduty_detector" "fail" {
  enable = false
}
