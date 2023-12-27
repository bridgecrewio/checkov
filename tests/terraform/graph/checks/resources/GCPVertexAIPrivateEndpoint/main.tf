resource "google_vertex_ai_endpoint" "endpoint_good" {
  name         = "good-endpoint"
  display_name = "good-endpoint"
  location     = "us-central1"
  region       = "us-central1"
  network      = "projects/${data.google_project.project.number}/global/networks/${google_compute_network.vertex_network.name}"
}

resource "google_vertex_ai_endpoint" "endpoint_bad" {
  name         = "good-endpoint"
  display_name = "good-endpoint"
  location     = "us-central1"
  region       = "us-central1"
}
