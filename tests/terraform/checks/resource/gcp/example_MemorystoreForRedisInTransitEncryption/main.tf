
resource "google_redis_instance" "pass" {
  provider       = google-beta
  name           = "mrr-memory-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 5

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"

  authorized_network = data.google_compute_network.redis-network.id

  redis_version      = "REDIS_6_X"
  display_name       = "Terraform Test Instance"
  reserved_ip_range  = "192.168.0.0/28"
  replica_count      = 5
  read_replicas_mode = "READ_REPLICAS_ENABLED"
  # auth_enabled=true
  labels = {
    my_key    = "my_val"
    other_key = "other_val"
  }
  transit_encryption_mode = "SERVER_AUTHENTICATION"
}

resource "google_redis_instance" "fail" {
  provider       = google-beta
  name           = "mrr-memory-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 5

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"

  authorized_network = data.google_compute_network.redis-network.id

  redis_version      = "REDIS_6_X"
  display_name       = "Terraform Test Instance"
  reserved_ip_range  = "192.168.0.0/28"
  replica_count      = 5
  read_replicas_mode = "READ_REPLICAS_ENABLED"
  # auth_enabled=true
  labels = {
    my_key    = "my_val"
    other_key = "other_val"
  }
  #   transit_encryption_mode = ""
}


resource "google_redis_instance" "fail2" {
  provider       = google-beta
  name           = "mrr-memory-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 5

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"

  authorized_network = data.google_compute_network.redis-network.id

  redis_version      = "REDIS_6_X"
  display_name       = "Terraform Test Instance"
  reserved_ip_range  = "192.168.0.0/28"
  replica_count      = 5
  read_replicas_mode = "READ_REPLICAS_ENABLED"
  # auth_enabled=true
  labels = {
    my_key    = "my_val"
    other_key = "other_val"
  }
     transit_encryption_mode = "DISABLED"
}