resource "google_kms_key_ring" "key_ring_good_1" {
  name = "key-ring-good1"
  location = "global"
}

resource "google_kms_key_ring" "key_ring_good_2" {
  name = "key-ring-good2"
  location = "global"
}

resource "google_kms_key_ring" "key_ring_bad_1" {
  name = "key-ring-bad1"
  location = "global"
}

resource "google_kms_key_ring" "key_ring_bad_2" {
  name = "key-ring-bad2"
  location = "global"
}

resource "google_kms_key_ring" "key_ring_bad_3" {
  name = "key-ring-bad3"
  location = "global"
}

resource "google_kms_key_ring" "key_ring_bad_4" {
  name = "key-ring-bad4"
  location = "global"
}

# Non-public IAM policies

resource "google_kms_key_ring_iam_member" "key_ring_iam_good1" {
  key_ring_id = google_kms_key_ring.key_ring_good_1.id
  role = "roles/cloudkms.cryptoKeyEncrypter"
  member = "user:jane@example.com"
}

resource "google_kms_key_ring_iam_binding" "key_ring_iam_good2" {
  key_ring_id = google_kms_key_ring.key_ring_good_2.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "user:jane@example.com",
  ]
}

# Public IAM policies

resource "google_kms_key_ring_iam_member" "key_ring_iam_bad_1" {
  key_ring_id = google_kms_key_ring.key_ring_bad_1.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "allUsers"
}

resource "google_kms_key_ring_iam_member" "key_ring_iam_bad_2" {
  key_ring_id = google_kms_key_ring.key_ring_bad_2.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "allAuthenticatedUsers"
}


resource "google_kms_key_ring_iam_binding" "key_ring_iam_bad_3" {
  key_ring_id = google_kms_key_ring.key_ring_bad_3.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "allUsers",
  ]
}

resource "google_kms_key_ring_iam_binding" "key_ring_iam_bad_4" {
  key_ring_id = google_kms_key_ring.key_ring_bad_4.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "allAuthenticatedUsers",
  ]
}
