resource "alicloud_slb_tls_cipher_policy" "fail" {
  tls_cipher_policy_name = "itsbaditsdverybad"
  tls_versions           = ["TLSv1.1","TLSv1.2"]
  ciphers                = ["AES256-SHA","AES256-SHA256", "AES128-GCM-SHA256"]
}

resource "alicloud_slb_tls_cipher_policy" "pass" {
  tls_cipher_policy_name = "itsfine"
  tls_versions           = ["TLSv1.2"]
  ciphers                = ["AES256-SHA","AES256-SHA256", "AES128-GCM-SHA256"]
}
