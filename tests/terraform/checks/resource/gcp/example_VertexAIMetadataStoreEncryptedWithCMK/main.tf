resource "google_vertex_ai_metadata_store" "fail" {
  name        = "test-store"
  description = "Store to test the terraform module"
  region      = "us-central1"
  #   encryption_spec {
  #       kms_key_name=
  #   }
}

resource "google_vertex_ai_metadata_store" "pass" {
  name        = "test-store"
  description = "Store to test the terraform module"
  region      = "us-central1"
     encryption_spec {
         kms_key_name=google_kms_crypto_key.example.name
     }
}