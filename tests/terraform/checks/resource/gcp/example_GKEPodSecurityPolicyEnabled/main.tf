resource "google_container_cluster" "unknown" {
}

resource "google_container_cluster" "unknown2" {
  min_master_version = "1.27"
}


resource "google_container_cluster" "pass" {
  min_master_version = "1.24"
  pod_security_policy_config {
    enabled = true
  }
}

resource "google_container_cluster" "fail" {
  min_master_version = "1.24"
}

resource "google_container_cluster" "fail2" {
  min_master_version = "1.24"
    pod_security_policy_config {
    enabled = false
  }
}

resource "google_container_cluster" "unknown3" {
  min_master_version = "not_a_float"
    pod_security_policy_config {
    enabled = false
  }
}



