
resource "aws_emr_block_public_access_configuration" "fail" {
  block_public_security_group_rules = false
}

resource "aws_emr_block_public_access_configuration" "pass" {
  block_public_security_group_rules = true
  permitted_public_security_group_rule_range {
    min_range = 22
    max_range = 22
  }

  permitted_public_security_group_rule_range {
    min_range = 100
    max_range = 101
  }
}
