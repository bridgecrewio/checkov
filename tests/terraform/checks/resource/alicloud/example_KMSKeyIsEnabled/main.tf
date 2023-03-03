resource "alicloud_kms_key" "pass" {
  description             = "Hello KMS"
  pending_window_in_days  = "7"
  status                  = "Enabled"
  automatic_rotation      = "Enabled"
}

resource "alicloud_kms_key" "fail" {
  description             = "Hello KMS"
  pending_window_in_days  = "7"
  status                  = "Disabled"
}

resource "alicloud_kms_key" "pass2" {
  description             = "Hello KMS"
  pending_window_in_days  = "7"
}
