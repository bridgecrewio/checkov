resource "google_kms_key_ring" "keyring" {
  name = "keyring-example"
  location = "global"
}


resource "google_kms_crypto_key" "key_good_1" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "key_bad_1" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "key_bad_2" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key_iam_member" "crypto_key_good" {
  crypto_key_id = google_kms_crypto_key.key_good_1.id
  role = "roles/cloudkms.cryptoKeyEncrypter"
  member = "user:jane@example.com"
}

resource "google_kms_crypto_key_iam_member" "crypto_key_bad_1" {
  crypto_key_id = google_kms_crypto_key.key_bad_1.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "allUsers"
}

resource "google_kms_crypto_key_iam_member" "crypto_key_bad_2" {
  crypto_key_id = google_kms_crypto_key.key_bad_2.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "allAuthenticatedUsers"
}

resource "google_kms_crypto_key" "key_good_2" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "key_bad_3" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "key_bad_4" {
  name = "crypto-key-example"
  key_ring = google_kms_key_ring.keyring.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}


resource "google_kms_crypto_key_iam_binding" "crypto_key" {
  crypto_key_id = google_kms_crypto_key.key_good_2.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_kms_crypto_key_iam_binding" "crypto_key" {
  crypto_key_id = google_kms_crypto_key.key_bad_3.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "allUsers",
  ]
}

resource "google_kms_crypto_key_iam_binding" "crypto_key" {
  crypto_key_id = google_kms_crypto_key.key_bad_4.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "allAuthenticatedUsers",
  ]
}
