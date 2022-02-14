resource "google_pubsub_topic" "fail" {
  name = "example-topic"
  # kms_key_name = google_kms_crypto_key.crypto_key.id
}

resource "google_pubsub_topic" "pass" {
  name         = "example-topic"
  kms_key_name = google_kms_crypto_key.crypto_key.id
}