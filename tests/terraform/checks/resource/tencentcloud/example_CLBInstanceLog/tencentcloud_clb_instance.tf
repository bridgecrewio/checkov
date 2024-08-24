# pass
resource "tencentcloud_clb_instance" "positive" {
  network_type                 = "INTERNAL"
  clb_name                     = "clb_example"
  project_id                   = 0
  vpc_id                       = tencentcloud_vpc.vpc_test.id
  subnet_id                    = tencentcloud_subnet.subnet_test.id
  load_balancer_pass_to_target = true
  log_set_id                   = tencentcloud_clb_log_set.set.id
  log_topic_id                 = tencentcloud_clb_log_topic.topic.id

  tags = {
    test = "tf"
  }
}

# failed
resource "tencentcloud_clb_instance" "negative" {
  network_type                 = "INTERNAL"
  clb_name                     = "clb_example"
  project_id                   = 0
  vpc_id                       = tencentcloud_vpc.vpc_test.id
  subnet_id                    = tencentcloud_subnet.subnet_test.id
  load_balancer_pass_to_target = true

  tags = {
    test = "tf"
  }
}