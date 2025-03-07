resource "awscc_kms_key" "pass1" {
  description             = "KMS key 1"
  pending_window_in_days = 10
  enable_key_rotation     = true
}

resource "awscc_kms_key" "pass2" {
  description              = "KMS key 1"
  pending_window_in_days  = 10
  key_spec = "SYMMETRIC_DEFAULT"
  enable_key_rotation      = true
}

resource "awscc_kms_key" "fail1" {
  description             = "KMS key 1"
  pending_window_in_days = 10
}

resource "awscc_kms_key" "fail2" {
  description             = "KMS key 1"
  pending_window_in_days = 10
  enable_key_rotation     = false
}

resource "awscc_kms_key" "fail3" {
  description              = "KMS key 1"
  pending_window_in_days  = 10
  key_spec = "SYMMETRIC_DEFAULT"
  enable_key_rotation      = false
}

resource "awscc_kms_key" "fail4" {
  description              = "KMS key 1"
  pending_window_in_days  = 10
  key_spec = "SYMMETRIC_DEFAULT"
}