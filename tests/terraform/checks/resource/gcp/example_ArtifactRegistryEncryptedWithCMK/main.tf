resource "google_artifact_registry_repository" "fail" {
  provider = google-beta

  location      = "us-central1"
  repository_id = "my-repository"
  description   = "example docker repository with cmek"
  format        = "DOCKER"
  #   kms_key_name = "kms-key"
}

resource "google_artifact_registry_repository" "pass" {
  provider = google-beta

  location      = "us-central1"
  repository_id = "my-repository"
  description   = "example docker repository with cmek"
  format        = "DOCKER"
  kms_key_name  = google_kms_crypto_key.example.name
}