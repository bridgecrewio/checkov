resource "google_bigquery_dataset" "fail" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "EU"
  default_table_expiration_ms = 3600000

  labels = {
    env = "default"
  }

  access {
    role          = "OWNER"
    special_group = "allAuthenticatedUsers"
  }

  access {
    role   = "READER"
    domain = "hashicorp.com"
  }
}

resource "google_bigquery_dataset" "pass" {
  dataset_id                  = var.dataset.dataset_id
  friendly_name               = var.dataset.friendly_name
  description                 = var.dataset.description
  location                    = var.location
  default_table_expiration_ms = var.dataset.default_table_expiration_ms

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.example.name
  }
}
