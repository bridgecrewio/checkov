resource "google_service_account" "account_ok" {
  account_id = "dev-foo-account"
}

resource "google_service_account_key" "ok_key" {
  service_account_id = google_service_account.account_ok.name
}

resource "google_service_account" "account_bad" {
  account_id = "dev-foo-account"
}
