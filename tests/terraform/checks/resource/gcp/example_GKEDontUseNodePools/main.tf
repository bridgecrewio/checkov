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

# When remove_default_node_pool = true the default node pool is destroyed
# immediately after cluster creation, so the inline node_pool block is a
# temporary scaffold required by the provider — not a long-lived pool.
# The check must pass in this case.
resource "google_container_cluster" "pass_remove_default" {
  name                     = "vincent-vega"
  location                 = "us-central1-a"
  initial_node_count       = 1
  remove_default_node_pool = true

  node_pool {
    node_config {
      service_account = google_service_account.default.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }
  }
}