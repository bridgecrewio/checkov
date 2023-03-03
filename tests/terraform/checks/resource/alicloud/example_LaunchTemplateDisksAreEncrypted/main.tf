
resource "alicloud_ecs_launch_template" "fail" {
  launch_template_name           = "tf_test_name"
  description                   = "Test For Terraform"
  image_id                      = "m-bp1i3ucxxxxx"
  host_name                     = "host_name"
  instance_charge_type          = "PrePaid"
  instance_name                 = "instance_name"
  instance_type                 = "ecs.instance_type"
  internet_charge_type          = "PayByBandwidth"
  internet_max_bandwidth_in     = "5"
  internet_max_bandwidth_out    = "0"
  io_optimized                  = "optimized"
  key_pair_name                 = "key_pair_name"
  ram_role_name                 = "ram_role_name"
  network_type                  = "vpc"
  security_enhancement_strategy = "Active"
  spot_price_limit              = "5"
  spot_strategy                 = "SpotWithPriceLimit"
  security_group_ids            = ["sg-zkdfjaxxxxxx"]
  system_disk {
    category             = "cloud_ssd"
    description          = "Test For Terraform"
    name                 = "tf_test_name"
    size                 = "40"
    delete_with_instance = "false"
  }

  resource_group_id = "rg-zkdfjaxxxxxx"
  user_data         = "xxxxxxx"
  vswitch_id        = "vw-zwxscaxxxxxx"
  vpc_id            = "vpc-asdfnbgxxxxxxx"
  zone_id           = "cn-hangzhou-i"

  template_tags = {
    Create = "Terraform"
    For    = "Test"
  }

  network_interfaces {
    name              = "eth0"
    description       = "hello1"
    primary_ip        = "10.0.0.2"
    security_group_id = "sg-asdfnbgxxxxxxx"
    vswitch_id        = "vw-zkdfjaxxxxxx"
  }

  data_disks {
    name                 = "disk1"
    description          = "test1"
    delete_with_instance = "true"
    category             = "cloud"
    encrypted            = "false"
    performance_level    = "PL0"
    size                 = "20"
  }
  data_disks {
    name                 = "disk2"
    description          = "test2"
    delete_with_instance = "true"
    category             = "cloud"
    encrypted            = "false"
    performance_level    = "PL0"
    size                 = "20"
  }
}

resource "alicloud_ecs_launch_template" "fail2" {
  launch_template_name           = "tf_test_name"
  description                   = "Test For Terraform"
  image_id                      = "m-bp1i3ucxxxxx"
  host_name                     = "host_name"
  instance_charge_type          = "PrePaid"
  instance_name                 = "instance_name"
  instance_type                 = "ecs.instance_type"
  internet_charge_type          = "PayByBandwidth"
  internet_max_bandwidth_in     = "5"
  internet_max_bandwidth_out    = "0"
  io_optimized                  = "optimized"
  key_pair_name                 = "key_pair_name"
  ram_role_name                 = "ram_role_name"
  network_type                  = "vpc"
  security_enhancement_strategy = "Active"
  spot_price_limit              = "5"
  spot_strategy                 = "SpotWithPriceLimit"
  security_group_ids            = ["sg-zkdfjaxxxxxx"]
  system_disk {
    category             = "cloud_ssd"
    description          = "Test For Terraform"
    name                 = "tf_test_name"
    size                 = "40"
    delete_with_instance = "false"
  }

  resource_group_id = "rg-zkdfjaxxxxxx"
  user_data         = "xxxxxxx"
  vswitch_id        = "vw-zwxscaxxxxxx"
  vpc_id            = "vpc-asdfnbgxxxxxxx"
  zone_id           = "cn-hangzhou-i"

  template_tags = {
    Create = "Terraform"
    For    = "Test"
  }

  network_interfaces {
    name              = "eth0"
    description       = "hello1"
    primary_ip        = "10.0.0.2"
    security_group_id = "sg-asdfnbgxxxxxxx"
    vswitch_id        = "vw-zkdfjaxxxxxx"
  }

  data_disks {
    name                 = "disk1"
    description          = "test1"
    delete_with_instance = "true"
    category             = "cloud"
    encrypted            = false
    performance_level    = "PL0"
    size                 = "20"
  }

}

resource "alicloud_ecs_launch_template" "fail3" {
  launch_template_name           = "tf_test_name"
  description                   = "Test For Terraform"
  image_id                      = "m-bp1i3ucxxxxx"
  host_name                     = "host_name"
  instance_charge_type          = "PrePaid"
  instance_name                 = "instance_name"
  instance_type                 = "ecs.instance_type"
  internet_charge_type          = "PayByBandwidth"
  internet_max_bandwidth_in     = "5"
  internet_max_bandwidth_out    = "0"
  io_optimized                  = "optimized"
  key_pair_name                 = "key_pair_name"
  ram_role_name                 = "ram_role_name"
  network_type                  = "vpc"
  security_enhancement_strategy = "Active"
  spot_price_limit              = "5"
  spot_strategy                 = "SpotWithPriceLimit"
  security_group_ids            = ["sg-zkdfjaxxxxxx"]
  system_disk {
    category             = "cloud_ssd"
    description          = "Test For Terraform"
    name                 = "tf_test_name"
    size                 = "40"
    delete_with_instance = "false"
  }

  resource_group_id = "rg-zkdfjaxxxxxx"
  user_data         = "xxxxxxx"
  vswitch_id        = "vw-zwxscaxxxxxx"
  vpc_id            = "vpc-asdfnbgxxxxxxx"
  zone_id           = "cn-hangzhou-i"

  template_tags = {
    Create = "Terraform"
    For    = "Test"
  }

  network_interfaces {
    name              = "eth0"
    description       = "hello1"
    primary_ip        = "10.0.0.2"
    security_group_id = "sg-asdfnbgxxxxxxx"
    vswitch_id        = "vw-zkdfjaxxxxxx"
  }

  data_disks {
    name                 = "disk1"
    description          = "test1"
    delete_with_instance = "true"
    category             = "cloud"
    performance_level    = "PL0"
    size                 = "20"
  }

}

resource "alicloud_ecs_launch_template" "pass" {
  launch_template_name          = "tf_test_name"
  description                   = "Test For Terraform"
  image_id                      = "m-bp1i3ucxxxxx"
  host_name                     = "host_name"
  instance_charge_type          = "PrePaid"
  instance_name                 = "instance_name"
  instance_type                 = "ecs.instance_type"
  internet_charge_type          = "PayByBandwidth"
  internet_max_bandwidth_in     = "5"
  internet_max_bandwidth_out    = "0"
  io_optimized                  = "optimized"
  key_pair_name                 = "key_pair_name"
  ram_role_name                 = "ram_role_name"
  network_type                  = "vpc"
  security_enhancement_strategy = "Active"
  spot_price_limit              = "5"
  spot_strategy                 = "SpotWithPriceLimit"
  security_group_ids            = ["sg-zkdfjaxxxxxx"]
  system_disk {
    category             = "cloud_ssd"
    description          = "Test For Terraform"
    name                 = "tf_test_name"
    size                 = "40"
    delete_with_instance = "false"
  }

  resource_group_id = "rg-zkdfjaxxxxxx"
  user_data         = "xxxxxxx"
  vswitch_id        = "vw-zwxscaxxxxxx"
  vpc_id            = "vpc-asdfnbgxxxxxxx"
  zone_id           = "cn-hangzhou-i"

  template_tags = {
    Create = "Terraform"
    For    = "Test"
  }

  network_interfaces {
    name              = "eth0"
    description       = "hello1"
    primary_ip        = "10.0.0.2"
    security_group_id = "sg-asdfnbgxxxxxxx"
    vswitch_id        = "vw-zkdfjaxxxxxx"
  }

  data_disks {
    name                 = "disk1"
    description          = "test1"
    delete_with_instance = "true"
    category             = "cloud"
    encrypted            = true
    performance_level    = "PL0"
    size                 = "20"
  }

  data_disks {
    name                 = "disk2"
    description          = "test2"
    delete_with_instance = "true"
    category             = "cloud"
    encrypted            = true
    performance_level    = "PL0"
    size                 = "20"
  }
}