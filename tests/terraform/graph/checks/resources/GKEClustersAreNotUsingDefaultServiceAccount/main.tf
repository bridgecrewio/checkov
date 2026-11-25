resource "google_service_account" "custom" {
  account_id   = "custom-sa"
  display_name = "Custom SA"
}

resource "google_project_default_service_accounts" "used" {
  project = "my-project-id"
  action  = "DELETE"
}

# No service_account set: the cluster runs on the Compute Engine default
# service account, the exact violation this check names.
resource "google_container_cluster" "bare" {
  name               = "bare-cluster"
  location           = "us-central1"
  initial_node_count = 1
}

resource "google_container_cluster" "custom" {
  name               = "custom-cluster"
  location           = "us-central1"
  initial_node_count = 1
  node_config {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = "custom-sa@my-project.iam.gserviceaccount.com"
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_cluster" "defemail" {
  name               = "default-email-cluster"
  location           = "us-central1"
  initial_node_count = 1
  node_config {
    service_account = "123456789-compute@developer.gserviceaccount.com"
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_cluster" "refdefault" {
  name               = "ref-default-cluster"
  location           = "us-central1"
  initial_node_count = 1
  node_config {
    service_account = google_project_default_service_accounts.used.id
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# The service account is a reference to a computed value that cannot be
# resolved statically, so the check returns no result for this cluster.
# That matches standard checkov behaviour for unrendered values.
resource "google_container_cluster" "refcustom" {
  name               = "ref-custom-cluster"
  location           = "us-central1"
  initial_node_count = 1
  node_config {
    service_account = google_service_account.custom.email
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# We can't create a cluster with no node pool defined, but we want to only use
# separately managed node pools. So we create the smallest possible default
# node pool and immediately delete it.
resource "google_container_cluster" "pools_custom" {
  name                     = "pools-custom-cluster"
  location                 = "us-central1"
  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "custom_pool" {
  name       = "custom-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.pools_custom.name
  node_count = 1
  node_config {
    service_account = "custom-sa@my-project.iam.gserviceaccount.com"
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_cluster" "pools_default" {
  name                     = "pools-default-cluster"
  location                 = "us-central1"
  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "default_pool" {
  name       = "default-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.pools_default.name
  node_count = 1
  node_config {
    machine_type = "e2-medium"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

resource "google_container_cluster" "pools_defemail" {
  name                     = "pools-defemail-cluster"
  location                 = "us-central1"
  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "defemail_pool" {
  name       = "defemail-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.pools_defemail.name
  node_count = 1
  node_config {
    service_account = "123456789-compute@developer.gserviceaccount.com"
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}
