resource "google_notebooks_instance" "instance_bad_vm" {
  name = "notebooks-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }
}

resource "google_notebooks_instance" "instance_bad_container" {
  name = "notebooks-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  metadata = {
    proxy-mode = "service_account"
    terraform  = "true"
  }
  container_image {
    repository = "gcr.io/deeplearning-platform-release/base-cpu"
    tag = "latest"
  }
}

resource "google_notebooks_instance" "instance_bad" {
  name = "notebooks-instance"
  location = "us-central1-a"
  machine_type = "e2-medium"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [ "my@service-account.com"]
  service_account = "my@service-account.com"

  install_gpu_driver = true
  boot_disk_type = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip = true
  no_proxy_access = true

  network = data.google_compute_network.my_network.id
  subnet = data.google_compute_subnetwork.my_subnetwork.id

  labels = {
    k = "val"
  }

  metadata = {
    terraform = "true"
  }
}

data "google_compute_network" "my_network" {
  name = "default"
}

data "google_compute_subnetwork" "my_subnetwork" {
  name   = "default"
  region = "us-central1"
}

resource "google_notebooks_instance" "instance_bad_crafty_container" {
  name = "notebooks-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  kms_key = var.kms_key
  metadata = {
    proxy-mode = "service_account"
    terraform  = "true"
  }
  container_image {
    repository = "gcr.io/deeplearning-platform-release/base-cpu"
    tag = "latest"
  }
}

resource "google_notebooks_instance" "instance_good_vm" {
  name = "notebooks-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  disk_encryption = "CMEK"
  kms_key = var.kms_key
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }
}
