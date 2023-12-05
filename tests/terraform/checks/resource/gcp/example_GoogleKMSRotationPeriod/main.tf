# pass

resource "google_kms_crypto_key" "ninety_days" {
  name            = "crypto-key-example"
  key_ring        = "google_kms_key_ring.keyring.id"
  rotation_period = "7776000s"
}

resource "google_kms_crypto_key" "minimum" {
  name            = "crypto-key-example"
  key_ring        = "google_kms_key_ring.keyring.id"
  rotation_period = "86400s"
}

# fail

resource "google_kms_crypto_key" "half_year" {
  name            = "crypto-key-example"
  key_ring        = "google_kms_key_ring.keyring.id"
  rotation_period = "15552000s"
}

resource "google_kms_crypto_key" "default" {
  name     = "crypto-key-example"
  key_ring = "google_kms_key_ring.keyring.id"
}

# unknown

resource "google_kms_crypto_key" "asymmetric" {
  name     = "crypto-key-example"
  key_ring = "google_kms_key_ring.keyring.id"
  purpose  = "ASYMMETRIC_SIGN"
}

resource "google_kms_crypto_key" "fail" {
  name            = "crypto-key-example"
  key_ring        = "google_kms_key_ring.keyring.id"
  rotation_period = 90
}