resource "aws_cloudtrail" "tfer--cashdash_trail" {
  enable_log_file_validation    = true
  enable_logging                = true
  include_global_service_events = true
  is_multi_region_trail         = true
  is_organization_trail         = false
  kms_key_id                    = "arn:aws:kms:us-east-1:098885917934:key/5e7c4a79-bd63-42ca-9ae0-8f8e41f9c2f1"
  name                          = "cashdash_trail"
  s3_bucket_name                = "cashdash-trail"
  sns_topic_name                = "arn:aws:sns:us-east-1:098885917934:clodtrail-sns-topic"
}

resource "google_compute_instance" "tfer--sentry-002D-v1" {
  attached_disk {
    device_name = "sentry"
    mode        = "READ_WRITE"
    source      = "https://www.googleapis.com/compute/v1/projects/be-base-wksp-v1/zones/us-west3-b/disks/sentry-data-v1"
  }
  boot_disk {
    auto_delete = "true"
    device_name = "persistent-disk-0"
    initialize_params {
      image = "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-10-buster-v20200910"
      size  = "10"
      type  = "pd-standard"
    }
    kms_key_self_link = "projects/acme-project/locations/global/keyRings/global-v1/cryptoKeys/global-disk-key"
    mode              = "READ_WRITE"
    source            = "https://www.googleapis.com/compute/v1/projects/acme-project/zones/us-west3-b/disks/sentry-v1"
  }
  can_ip_forward      = "false"
  deletion_protection = "false"
  enable_display      = "false"
  machine_type        = "n1-standard-2"
  metadata = {
    block-project-ssh-keys = "true"
    some-other-attribute   = "false"
  }
  name                    = "sentry-v1"
  network_interface {
    access_config {
      nat_ip       = "34.106.48.192"
      network_tier = "PREMIUM"
    }
    network            = "https://www.googleapis.com/compute/v1/projects/acme-project/global/networks/acme"
    network_ip         = "10.40.0.53"
    subnetwork         = "https://www.googleapis.com/compute/v1/projects/acme-project/regions/us-west3/subnetworks/sentry"
    subnetwork_project = "acme-project"
  }
  project = "acme-project"
  scheduling {
    automatic_restart   = "true"
    on_host_maintenance = "MIGRATE"
    preemptible         = "false"
  }
  service_account {
    email  = "sentry-vm@acme-project.iam.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/devstorage.read_only"]
  }
  shielded_instance_config {
    enable_integrity_monitoring = "true"
    enable_secure_boot          = "false"
    enable_vtpm                 = "true"
  }
  tags = ["allow-ssh", "allow-sentry"]
  zone = "us-west3-b"
}
