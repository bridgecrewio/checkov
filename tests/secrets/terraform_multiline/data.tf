data "google_secret_manager_secret_version" "secret" {
  secret = "somesecretid"
}
