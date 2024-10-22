resource "google_vertex_ai_featurestore" "featurestore_good" {
  name     = "terraform"
  labels = {
    foo = "bar"
  }
  region   = "us-central1"
  online_serving_config {
    fixed_node_count = 2
  }
  encryption_spec {
    kms_key_name = "kms-name"
  }
  force_destroy = true
}

resource "google_vertex_ai_featurestore" "featurestore_bad" {
  name     = "terraform"
  labels = {
    foo = "bar"
  }
  region   = "us-central1"
  online_serving_config {
    fixed_node_count = 2
  }
  force_destroy = true
}