resource "google_vertex_ai_tensorboard" "tensorboard_bad" {
  display_name = "terraform"
  description  = "sample description"
  labels       = {
    "key1" : "value1",
    "key2" : "value2"
  }
  region       = "us-central1"
}

resource "google_vertex_ai_tensorboard" "tensorboard_good" {
  display_name = "terraform"
  description  = "sample description"
  labels       = {
    "key1" : "value1",
    "key2" : "value2"
  }
  region       = "us-central1"
  encryption_spec {
    kms_key_name = "some_key"
  }
}
