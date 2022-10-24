
# Passes b/c we enabled AUTH
resource "google_redis_instance" "pass" {
  name           = "my-pass-instance"
  memory_size_gb = 1
  tier           = "STANDARD_HA"

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"
  redis_version           = "REDIS_6_X"

  labels = {
    foo = "bar"
  }

  auth_enabled = true
}

# Fails b/c "auth_enabled" does not exist
# AUTH is not enabled by default
resource "google_redis_instance" "fail1" {
  name           = "my-fail-instance1"
  tier           = "STANDARD_HA"
  memory_size_gb = 1

  location_id             = "us-central1-a"
  alternative_location_id = "us-central1-f"

  redis_version = "REDIS_4_0"
  display_name  = "I am insecure"

  maintenance_policy {
    weekly_maintenance_window {
      day = "TUESDAY"
      start_time {
        hours   = 0
        minutes = 30
        seconds = 0
        nanos   = 0
      }
    }
  }
}

# Fails b/c we turn off AUTH
resource "google_redis_instance" "fail2" {
  name           = "my-fail-instance2"
  memory_size_gb = 1

  auth_enabled = false
}
