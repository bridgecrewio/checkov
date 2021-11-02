resource "google_service_account" "account_ok" {
  account_id = "dev-foo-account"
}

resource "google_service_account" "account_bad" {
  account_id = "dev-foo-account"
}

resource "google_service_account_key" "account_bad" {
  service_account_id = google_service_account.account_bad.name
}
