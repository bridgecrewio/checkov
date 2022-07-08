
provider "alicloud" {
}

#happy path
resource "alicloud_cs_kubernetes" "pass" {
  worker_number         = 4
  worker_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  worker_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]

  addons {
    config = ""
    name   = "terway-eniip"
  }

  pod_vswitch_ids = ["vsw-id4"]
}

# array of addons
resource "alicloud_cs_kubernetes" "pass2" {
  worker_number         = 4
  worker_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  worker_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]

  addons {
    config = ""
    name   = "flannel"
  }

  addons {
    name   = "csi-plugin"
    config = ""
  }

  pod_cidr = "10.0.1.0/16"
}


#no addon
resource "alicloud_cs_kubernetes" "fail" {
  worker_number         = 4
  worker_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_vswitch_ids    = ["vsw-id1", "vsw-id2", "vsw-id3"]
  master_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  worker_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]

  pod_vswitch_ids = ["vsw-id6"]
}

#conflict with worker_vswitch_ids
resource "alicloud_cs_kubernetes" "fail2" {
  worker_number         = 4
  worker_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_vswitch_ids    = ["vsw-id2", "vsw-id2", "vsw-id3"]
  master_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  worker_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  addons {
    config = ""
    name   = "terway-eniip"
  }
  pod_vswitch_ids = ["vsw-id1"]
}

#conflict with master_vswitch_ids
resource "alicloud_cs_kubernetes" "fail3" {
  worker_number         = 4
  worker_vswitch_ids    = ["vsw-id1", "vsw-id1", "vsw-id3"]
  master_vswitch_ids    = ["vsw-id1", "vsw-id2", "vsw-id3"]
  master_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]
  worker_instance_types = ["ecs.n4.small", "ecs.sn1ne.xlarge", "ecs.n4.xlarge"]

  addons {
    config = ""
    name   = "terway-eniip"
  }
  pod_vswitch_ids = ["vsw-id2"]
}

