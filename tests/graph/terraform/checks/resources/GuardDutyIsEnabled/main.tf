resource "aws_guardduty_detector" "ok" {
  enable = true
}

resource "aws_guardduty_detector" "not_ok" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "example" {
  auto_enable = true
  detector_id = aws_guardduty_detector.ok.id
}

resource "aws_guardduty_detector" "not_ok_false" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "example" {
  auto_enable = false
  detector_id = aws_guardduty_detector.not_ok_false.id
}