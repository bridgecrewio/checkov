resource "google_service_account" "account" {
  account_id = "dev-foo-account"
}

resource "google_service_account_key" "account_ok" {
  service_account_id = google_service_account.account.name
}

resource "google_service_account_key" "account_bad" {
  service_account_id = google_service_account.account.name
  public_key_data = "foo"
}
