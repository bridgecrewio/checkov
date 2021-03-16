# pass

resource "aws_ebs_encryption_by_default" "enabled" {
  enabled = true
}

resource "aws_ebs_encryption_by_default" "default" {
}

# failure

resource "aws_ebs_encryption_by_default" "disabled" {
  enabled = false
}
