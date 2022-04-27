# pass
resource "yandex_kms_symmetric_key" "pass" {
  name              = "example-symmetric-key"
  description       = "description for key"
  default_algorithm = "AES_128"
  rotation_period   = "8760h" 
}

# fail
resource "yandex_kms_symmetric_key" "fail" {
  name              = "example-symmetric-key"
  description       = "description for key"
  default_algorithm = "AES_128"
}