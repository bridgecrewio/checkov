resource "google_tpu_v2_vm" "tpu_good" {
  name = "good-tpu"
  zone = "us-central1-c"

  runtime_version  = "tpu-vm-tf-2.13.0"

  accelerator_config {
    type     = "V2"
    topology = "2x2"
  }

  cidr_block = "10.0.0.0/29"

  network_config {
    can_ip_forward      = true
    enable_external_ips = false
  }
}

resource "google_tpu_v2_vm" "tpu_bad" {
  name = "good-tpu"
  zone = "us-central1-c"

  runtime_version  = "tpu-vm-tf-2.13.0"

  accelerator_config {
    type     = "V2"
    topology = "2x2"
  }

  cidr_block = "10.0.0.0/29"

  network_config {
    can_ip_forward      = true
    enable_external_ips = true
  }
}

resource "google_tpu_v2_vm" "tpu_bad_unset" {
  name = "good-tpu"
  zone = "us-central1-c"

  runtime_version  = "tpu-vm-tf-2.13.0"

  accelerator_config {
    type     = "V2"
    topology = "2x2"
  }

  cidr_block = "10.0.0.0/29"

  network_config {
    can_ip_forward      = true
  }
}