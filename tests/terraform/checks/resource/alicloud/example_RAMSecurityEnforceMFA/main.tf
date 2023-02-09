resource "alicloud_ram_security_preference" "fail" {
  enable_save_mfa_ticket        = false
  allow_user_to_change_password = true
  enforce_mfa_for_login         = false
}

resource "alicloud_ram_security_preference" "fail2" {
  enable_save_mfa_ticket        = false
  allow_user_to_change_password = true
}

resource "alicloud_ram_security_preference" "pass" {
  enable_save_mfa_ticket        = false
  allow_user_to_change_password = true
  enforce_mfa_for_login         = true
}