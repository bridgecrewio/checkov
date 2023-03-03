
resource "google_container_cluster" "fail2" {
  name               = "marcellus-wallace"
  location           = "us-central1-a"
  initial_node_count = 3

  master_auth {
    username = ""

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  timeouts {
    create = "30m"
    update = "40m"
  }
}

resource "google_container_cluster" "fail" {
  name               = "google_cluster_bad"
  monitoring_service = "none"
  enable_legacy_abac = True
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "The world"
    }
  }

  master_auth {
    username = "test"
    password = "password"
  }

}

resource "google_container_cluster" "pass" {
  name               = "google_cluster"
  monitoring_service = "monitoring.googleapis.com"
  master_authorized_networks_config {}
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

resource "google_container_cluster" "pass2" {
  name               = "google_cluster"
  monitoring_service = "monitoring.googleapis.com"
  master_authorized_networks_config {}
  master_auth {
    username = ""
    password = ""
    client_certificate_config {
      issue_client_certificate = false
    }
  }

}

resource "google_container_cluster" "pass3" {
  name               = "marcellus-wallace"
  location           = "us-central1-a"
  initial_node_count = 3

  timeouts {
    create = "30m"
    update = "40m"
  }
}
