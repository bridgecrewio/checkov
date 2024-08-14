# pass
resource "tencentcloud_kubernetes_cluster" "positive" {
  vpc_id                  = tencentcloud_vpc.vpc.id
  cluster_max_pod_num     = 32
  cluster_name            = "test"
  cluster_desc            = "test cluster desc"
  cluster_max_service_num = 256
  cluster_internet        = true
  cluster_deploy_type     = "MANAGED_CLUSTER"
  network_type            = "VPC-CNI"
  eni_subnet_ids          = ["subnet-bk1etlyu"]
  service_cidr            = "10.1.0.0/24"

  worker_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-7"
    instance_type              = "S2.LARGE16"
    system_disk_type           = "CLOUD_PREMIUM"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    public_ip_assigned         = true
    subnet_id                  = "subnet-t5dv27rs"

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
  }

  log_agent {
    enabled = true
  }

  labels = {
    "test1" = "test1",
    "test2" = "test2",
  }
}

# failed
resource "tencentcloud_kubernetes_cluster" "negative" {
  vpc_id                  = tencentcloud_vpc.vpc.id
  cluster_max_pod_num     = 32
  cluster_name            = "test"
  cluster_desc            = "test cluster desc"
  cluster_max_service_num = 256
  cluster_internet        = true
  cluster_deploy_type     = "MANAGED_CLUSTER"
  network_type            = "VPC-CNI"
  eni_subnet_ids          = ["subnet-bk1etlyu"]
  service_cidr            = "10.1.0.0/24"

  worker_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-7"
    instance_type              = "S2.LARGE16"
    system_disk_type           = "CLOUD_PREMIUM"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    public_ip_assigned         = true
    subnet_id                  = "subnet-t5dv27rs"

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
  }

  log_agent {
    enabled = false
  }

  labels = {
    "test1" = "test1",
    "test2" = "test2",
  }
}