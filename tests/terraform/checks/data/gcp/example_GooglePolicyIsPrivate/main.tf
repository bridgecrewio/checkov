data "google_iam_policy" "pass" {
  binding {
    role = "roles/cloudkms.cryptoKeyEncrypter"

    members = [
      "user:jane@example.com",
    ]
  }
}

data "google_iam_policy" "fail" {
  binding {
    role = "roles/cloudkms.cryptoKeyEncrypter"

    members = [
      "allUsers",
    ]
  }
}