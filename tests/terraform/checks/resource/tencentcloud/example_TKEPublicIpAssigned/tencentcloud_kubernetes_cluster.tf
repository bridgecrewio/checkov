# pass
resource "tencentcloud_kubernetes_cluster" "positive1" {
  vpc_id                          = local.first_vpc_id
  cluster_cidr                    = "10.31.0.0/16"
  cluster_max_pod_num             = 32
  cluster_name                    = "tf_example_cluster"
  cluster_desc                    = "example for tke cluster"
  cluster_max_service_num         = 32
  cluster_internet                = true
  cluster_internet_security_group = local.sg_id
  cluster_version                 = "1.22.5"
  cluster_deploy_type             = "MANAGED_CLUSTER"

  master_config {
    count                = 1
    availability_zone    = "ap-guangzhou-3"
    instance_type        = "SA2.2XLARGE16"
    system_disk_type     = "CLOUD_SSD"
    system_disk_size     = 60
    internet_charge_type = "TRAFFIC_POSTPAID_BY_HOUR"
    subnet_id            = local.first_subnet_id
    img_id               = local.image_id

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    user_data                 = "dGVzdA=="
  }

  worker_config {
    count                = 1
    availability_zone    = "ap-guangzhou-4"
    instance_type        = "SA2.2XLARGE16"
    system_disk_type     = "CLOUD_SSD"
    system_disk_size     = 60
    internet_charge_type = "TRAFFIC_POSTPAID_BY_HOUR"
    subnet_id            = local.second_subnet_id

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    cam_role_name             = "CVM_QcsRole"
  }
}

resource "tencentcloud_kubernetes_cluster" "positive2" {
  vpc_id                          = local.first_vpc_id
  cluster_cidr                    = "10.31.0.0/16"
  cluster_max_pod_num             = 32
  cluster_name                    = "tf_example_cluster"
  cluster_desc                    = "example for tke cluster"
  cluster_max_service_num         = 32
  cluster_internet                = true
  cluster_internet_security_group = local.sg_id
  cluster_version                 = "1.22.5"
  cluster_deploy_type             = "MANAGED_CLUSTER"

  master_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-3"
    instance_type              = "SA2.2XLARGE16"
    system_disk_type           = "CLOUD_SSD"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    subnet_id                  = local.first_subnet_id
    img_id                     = local.image_id
    public_ip_assigned         = false

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    user_data                 = "dGVzdA=="
  }

  worker_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-4"
    instance_type              = "SA2.2XLARGE16"
    system_disk_type           = "CLOUD_SSD"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    subnet_id                  = local.second_subnet_id
    public_ip_assigned         = false

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    cam_role_name             = "CVM_QcsRole"
  }
}

# failed
resource "tencentcloud_kubernetes_cluster" "negative" {
  vpc_id                          = local.first_vpc_id
  cluster_cidr                    = "10.31.0.0/16"
  cluster_max_pod_num             = 32
  cluster_name                    = "tf_example_cluster"
  cluster_desc                    = "example for tke cluster"
  cluster_max_service_num         = 32
  cluster_internet                = true
  cluster_internet_security_group = local.sg_id
  cluster_version                 = "1.22.5"
  cluster_deploy_type             = "MANAGED_CLUSTER"

  master_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-3"
    instance_type              = "SA2.2XLARGE16"
    system_disk_type           = "CLOUD_SSD"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    subnet_id                  = local.first_subnet_id
    img_id                     = local.image_id
    public_ip_assigned         = true

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    user_data                 = "dGVzdA=="
  }

  worker_config {
    count                      = 1
    availability_zone          = "ap-guangzhou-4"
    instance_type              = "SA2.2XLARGE16"
    system_disk_type           = "CLOUD_SSD"
    system_disk_size           = 60
    internet_charge_type       = "TRAFFIC_POSTPAID_BY_HOUR"
    internet_max_bandwidth_out = 100
    subnet_id                  = local.second_subnet_id
    public_ip_assigned         = true

    data_disk {
      disk_type = "CLOUD_PREMIUM"
      disk_size = 50
    }

    enhanced_security_service = false
    enhanced_monitor_service  = false
    cam_role_name             = "CVM_QcsRole"
  }
}
