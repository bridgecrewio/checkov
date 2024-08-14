# pass
resource "tencentcloud_vpc_flow_log_config" "positive" {
  flow_log_id = tencentcloud_vpc_flow_log.example.id
  enable      = true
}

# failed
resource "tencentcloud_vpc_flow_log_config" "negative" {
  flow_log_id = tencentcloud_vpc_flow_log.example.id
  enable      = false
}