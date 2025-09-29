
resource "google_redis_instance" "fail" {
  name           = "fail-instance"
  connect_mode   = "DIRECT_PEERING"
}

resource "google_redis_instance" "pass" {
  name           = "pass-instance"
  connect_mode   = "PRIVATE_SERVICE_ACCESS"
}
