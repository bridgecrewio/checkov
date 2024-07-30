resource "google_container_cluster" "pass" {
  name               = "marcellus-wallace"
  location           = "us-central1-a"
  initial_node_count = 3
  node_config {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = google_service_account.default.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    labels = {
      foo = "bar"
    }
    tags = ["foo", "bar"]
  }
  timeouts {
    create = "30m"
    update = "40m"
  }
}

resource "google_container_cluster" "fail" {
  name               = "theDude"
  location           = "us-central1-a"
  initial_node_count = 3

  node_pool {
    node_config {
      # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
      service_account = google_service_account.default.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
      labels = {
        foo = "bar"
      }
      tags = ["foo", "bar"]
    }
  }

  timeouts {
    create = "30m"
    update = "40m"
  }
}