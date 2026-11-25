locals {
  project_id = data.google_project.project.project_id
}

# ---------------------------------------------------------------------------
# PASS: dedicated Autopilot cluster
# ---------------------------------------------------------------------------

resource "google_container_cluster" "autopilot" {
  name     = "ckv-gcp-69-autopilot"
  location = var.location
  project  = local.project_id

  network    = var.network
  subnetwork = var.subnetwork

  enable_autopilot    = true
  deletion_protection = false
}

# ---------------------------------------------------------------------------
# PASS: current workload metadata syntax on the cluster default node pool
# ---------------------------------------------------------------------------

resource "google_container_cluster" "current_metadata_mode" {
  name               = "ckv-gcp-69-current-mode"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  workload_identity_config {
    workload_pool = "${local.project_id}.svc.id.goog"
  }

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# ---------------------------------------------------------------------------
# PASS: legacy workload metadata syntax on the cluster default node pool
# ---------------------------------------------------------------------------

resource "google_container_cluster" "legacy_metadata_mode" {
  name               = "ckv-gcp-69-legacy-mode"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  workload_identity_config {
    workload_pool = "${local.project_id}.svc.id.goog"
  }

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }
}

# ---------------------------------------------------------------------------
# FAIL: Autopilot is explicitly disabled and there is no node metadata config
# ---------------------------------------------------------------------------

resource "google_container_cluster" "autopilot_disabled" {
  name               = "ckv-gcp-69-autopilot-disabled"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  enable_autopilot    = false
  deletion_protection = false
}

# ---------------------------------------------------------------------------
# FAIL: current workload metadata syntax explicitly selects GCE metadata
# ---------------------------------------------------------------------------

resource "google_container_cluster" "gce_metadata_mode" {
  name               = "ckv-gcp-69-gce-mode"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      mode = "GCE_METADATA"
    }
  }
}

# ---------------------------------------------------------------------------
# FAIL: node_config is omitted
# ---------------------------------------------------------------------------

resource "google_container_cluster" "node_config_omitted" {
  name               = "ckv-gcp-69-node-config-omitted"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false
}

# ---------------------------------------------------------------------------
# FAIL: node_config exists, but workload_metadata_config is omitted
# ---------------------------------------------------------------------------

resource "google_container_cluster" "workload_metadata_config_omitted" {
  name               = "ckv-gcp-69-metadata-config-omitted"
  location           = var.location
  project            = local.project_id
  initial_node_count = 1

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    # workload_metadata_config intentionally omitted.
  }
}

# ---------------------------------------------------------------------------
# PASS: current syntax on a separately managed node pool
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "current_metadata_mode" {
  project  = local.project_id
  name     = "ckv-gcp-69-pool-current"
  location = var.location
  cluster  = google_container_cluster.current_metadata_mode.name

  node_count = var.node_pool["node_count"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# ---------------------------------------------------------------------------
# PASS: legacy syntax on a separately managed node pool
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "legacy_metadata_mode" {
  project  = local.project_id
  name     = "ckv-gcp-69-pool-legacy"
  location = var.location
  cluster  = google_container_cluster.current_metadata_mode.name

  node_count = var.node_pool["node_count"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }
}

# ---------------------------------------------------------------------------
# FAIL: current syntax explicitly selects GCE metadata
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "gce_metadata_mode" {
  project  = local.project_id
  name     = "ckv-gcp-69-pool-gce"
  location = var.location
  cluster  = google_container_cluster.current_metadata_mode.name

  node_count = var.node_pool["node_count"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    workload_metadata_config {
      mode = "GCE_METADATA"
    }
  }
}

# ---------------------------------------------------------------------------
# FAIL: node_config is omitted
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "node_config_omitted" {
  project  = local.project_id
  name     = "ckv-gcp-69-pool-node-config-omitted"
  location = var.location
  cluster  = google_container_cluster.current_metadata_mode.name

  node_count = var.node_pool["node_count"]

  # node_config intentionally omitted.
}

# ---------------------------------------------------------------------------
# FAIL: node_config exists, but workload_metadata_config is omitted
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "workload_metadata_config_omitted" {
  project  = local.project_id
  name     = "ckv-gcp-69-pool-metadata-config-omitted"
  location = var.location
  cluster  = google_container_cluster.current_metadata_mode.name

  node_count = var.node_pool["node_count"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    # workload_metadata_config intentionally omitted.
  }
}