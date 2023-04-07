# FAIL 1: node_locations count not greater than 3

resource "google_container_cluster" "fail_1" {
  name               = "example-cluster"
  location           = "us-central1"
  initial_node_count = 3

  node_config {
    machine_type = "n1-standard-2"
  }

  node_locations = ["us-central1-a", "us-central1-b"]

}

# FAIL 2: 

resource "google_container_cluster" "fail_2" {
  name               = "example-cluster"
#   location           = "us-central1"
  initial_node_count = 3

  node_config {
    machine_type = "n1-standard-2"
  }

  node_locations = ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]

}

# PASS: All checks passsed

resource "google_container_cluster" "pass_1" {
  name               = "example-cluster"
  location           = "us-central1"
  initial_node_count = 3

  node_config {
    machine_type = "n1-standard-2"
  }

  node_locations = ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]

}

# PASS 2: node_locations count equals to 3

resource "google_container_cluster" "pass_2" {
  name               = "example-cluster"
  location           = "us-central1"
  initial_node_count = 3

  node_config {
    machine_type = "n1-standard-2"
  }

  node_locations = ["us-central1-a", "us-central1-b", "us-central1-c"]

}