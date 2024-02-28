resource "google_vertex_ai_index_endpoint" "index_endpoint_good" {
  display_name = "good-endpoint"
  description  = "A good vertex endpoint"
  region       = "us-central1"

  private_service_connect_config {
    enable_private_service_connect = true
    project_allowlist = [
        data.google_project.project.number,
    ]
  }
}

resource "google_vertex_ai_index_endpoint" "index_endpoint_good_explicit" {
  display_name = "good-explicit-endpoint"
  description  = "A good vertex endpoint"
  region       = "us-central1"

  public_endpoint_enabled = false
}

resource "google_vertex_ai_index_endpoint" "index_endpoint_bad" {
  display_name = "bad-endpoint"
  description  = "A bad vertex endpoint"
  region       = "us-central1"
  public_endpoint_enabled = true
}