
resource "google_dataproc_cluster" "pass1" {
  name   = "my-pass-cluster"
  region = "us-central1"

  cluster_config {
    gce_cluster_config {
      zone = "us-central1-a"
      # no public IPs
      internal_ip_only = true
    }

    master_config {
      accelerators {
        accelerator_type  = "nvidia-tesla-k80"
        accelerator_count = "1"
      }
    }
  }
}


resource "google_dataproc_cluster" "fail1" {
  name   = "my-fail1-cluster"
  region = "us-central1"

  cluster_config {
    gce_cluster_config {
      zone = "us-central1-a"
      # "internal_ip_only" does not exist
      # and the default is public IPs
    }

    master_config {
      accelerators {
        accelerator_type  = "nvidia-tesla-k80"
        accelerator_count = "1"
      }
    }
  }
}

resource "google_dataproc_cluster" "fail2" {
  name   = "my-fail2-cluster"
  region = "us-central1"

  cluster_config {
    gce_cluster_config {
      zone = "us-central1-a"
      # "internal_ip_only" exists but it is set to false
      # public IPs are assigned
      internal_ip_only = false
    }

    master_config {
      accelerators {
        accelerator_type  = "nvidia-tesla-k80"
        accelerator_count = "1"
      }
    }
  }
}
