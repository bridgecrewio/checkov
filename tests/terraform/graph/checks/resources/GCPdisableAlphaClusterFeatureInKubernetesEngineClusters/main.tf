resource "google_container_cluster" "pass" {
  name               = "pud-example-rg"
  location           = "us-central1-a"
  enable_kubernetes_alpha = true
  node_pool {
    name               = "default-pool"
    initial_node_count = 1
    management {
      auto_repair = false
      auto_upgrade = false
    }
  }
  remove_default_node_pool = true
  release_channel {
    channel = "UNSPECIFIED"
  }
}


resource "google_container_cluster" "fail_1" {
  name               = "pud-example-rg"
  location           = "us-central1-a"
#   enable_kubernetes_alpha = true
  node_pool {
    name               = "default-pool"
    initial_node_count = 1
    management {
      auto_repair = false
      auto_upgrade = false
    }
  }
  remove_default_node_pool = true
  release_channel {
    channel = "UNSPECIFIED"
  }
}

resource "google_container_cluster" "fail_2" {
  name               = "pud-example-rg"
  location           = "us-central1-a"
  enable_kubernetes_alpha = false
  node_pool {
    name               = "default-pool"
    initial_node_count = 1
    management {
      auto_repair = false
      auto_upgrade = false
    }
  }
  remove_default_node_pool = true
  release_channel {
    channel = "UNSPECIFIED"
  }
}
