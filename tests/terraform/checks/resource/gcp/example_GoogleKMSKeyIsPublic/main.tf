#data "google_iam_policy" "fail_access" {
#  binding {
#    role    = "roles/cloudkms.cryptoKeyEncrypter"
#    members = ["allUsers"]
#  }
#}

resource "google_kms_crypto_key_iam_policy" "fail" {
  crypto_key_id = google_kms_crypto_key.positive1.id
  policy_data = jsonencode({

    bindings = [{
      role    = "roles/cloudkms.cryptoKeyEncrypter"
      members = ["allUsers"]
  }] })
}

#data "google_iam_policy" "pass_access" {
#  binding {
#    role    = "roles/cloudkms.cryptoKeyEncrypter"
#    members = ["jameswoolfenden"]
#  }
#}

resource "google_kms_crypto_key_iam_policy" "pass" {
  crypto_key_id = google_kms_crypto_key.pass.id
  policy_data = jsonencode({
    bindings = [
      {
        role    = "roles/cloudkms.cryptoKeyEncrypter"
        members = ["jameswoolfenden"]
  }] })
}

resource "google_kms_crypto_key_iam_policy" "fail2" {
  crypto_key_id = google_kms_crypto_key.pass.id
  policy_data = jsonencode({
    bindings = [
      {
        members = [
          "user:jane@example.com",
        ]
        role = "roles/cloudkms.admin"
      },
      {
        members = [
          "allAuthenticatedUsers",
        ]
        role = "roles/cloudkms.cryptoKeyDecrypter"
      },
    ]
  })
}

resource "google_kms_crypto_key_iam_policy" "pass2" {
  crypto_key_id = google_kms_crypto_key.pass.id
  policy_data   = <<HERE
{
    "bindings": [{
      "role": "roles/cloudkms.cryptoKeyEncrypter",
      "members": ["user:jameswoolfeden"]
    }]
}
HERE
}


resource "google_kms_crypto_key_iam_policy" "pass3" {
  crypto_key_id = google_kms_crypto_key.pass.id
  policy_data   = <<HERE
    "bindings"
HERE
}


resource "google_kms_crypto_key_iam_binding" "pass" {
  crypto_key_id = google_kms_crypto_key.key.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_kms_crypto_key_iam_binding" "fail" {
  crypto_key_id = google_kms_crypto_key.key.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"

  members = [
    "allUsers",
  ]
}

resource "google_kms_crypto_key_iam_member" "pass" {
  crypto_key_id = google_kms_crypto_key.key.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "user:jane@example.com"
}

resource "google_kms_crypto_key_iam_member" "fail" {
  crypto_key_id = google_kms_crypto_key.key.id
  role          = "roles/cloudkms.cryptoKeyEncrypter"
  member        = "allUsers"
}