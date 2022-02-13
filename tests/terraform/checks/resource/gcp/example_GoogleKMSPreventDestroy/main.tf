resource "google_kms_crypto_key" "pass" {
  name            = "crypto-key-example"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = "15552000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "fail" {
  name            = "crypto-key-example"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = "15552000s"

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_kms_crypto_key" "fail2" {
  name            = "crypto-key-example"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = "15552000s"
}