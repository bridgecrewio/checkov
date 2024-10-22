resource "google_bigtable_instance" "fail" {
  name = "tf-instance"

  cluster {
    cluster_id   = "tf-instance-cluster"
    num_nodes    = 1
    storage_type = "HDD"
    # kms_key_name = "some value"
  }

  labels = {
    my-label = "prod-label"
  }
}

resource "google_bigtable_instance" "fail2" {
  name = "tf-instance"
  deletion_protection = false
  cluster {
    cluster_id   = "tf-instance-cluster"
    num_nodes    = 1
    storage_type = "HDD"
    # kms_key_name = "some value"
  }

  labels = {
    my-label = "prod-label"
  }
}

resource "google_bigtable_instance" "pass" {
  name = "tf-instance"
  deletion_protection = true
  cluster {
    cluster_id   = "tf-instance-cluster"
    num_nodes    = 1
    storage_type = "HDD"
    kms_key_name = google_kms_crypto_key.example.name
  }

  labels = {
    my-label = "prod-label"
  }
}