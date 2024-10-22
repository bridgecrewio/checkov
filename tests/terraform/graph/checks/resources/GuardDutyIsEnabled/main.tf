# pass

resource "aws_guardduty_detector" "ok_old" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "ok_old" {
  auto_enable = true
  detector_id = aws_guardduty_detector.ok_old.id
}

resource "aws_guardduty_detector" "all" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "all" {
  auto_enable_organization_members = "ALL"
  detector_id                      = aws_guardduty_detector.all.id
}

# fail

resource "aws_guardduty_detector" "not_ok" {
  enable = true
}

resource "aws_guardduty_detector" "not_ok_false_old" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "not_ok_false_old" {
  auto_enable = false
  detector_id = aws_guardduty_detector.not_ok_false_old.id
}

resource "aws_guardduty_detector" "none" {
  enable = true
}

resource "aws_guardduty_organization_configuration" "none" {
  auto_enable_organization_members = "NONE"
  detector_id                      = aws_guardduty_detector.none.id
}
