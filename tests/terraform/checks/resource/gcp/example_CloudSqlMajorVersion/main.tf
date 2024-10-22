resource "google_sql_database_instance" "fail" {
  provider = google-beta

  name             = "private-instance-${random_id.db_name_suffix.hex}"
  region           = "us-central1"
  database_version = "MYSQL_5_7"

  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.private_network.id
    }
  }
}
resource "google_sql_database_instance" "pass" {
  provider = google-beta

  name             = "private-instance-${random_id.db_name_suffix.hex}"
  region           = "us-central1"
  database_version = "MYSQL_8_0"

  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.private_network.id
    }
  }
}

resource "google_sql_database_instance" "fail2" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    ip_configuration {
      require_ssl  = false
      ipv4_enabled = true
      authorized_networks {
        value = "108.12.12.0/24"
        name  = "internal"
      }

      authorized_networks {
        value = "0.0.0.0/0"
        name  = "internet"
      }
    }
    backup_configuration {
      enabled = false
    }
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    database_flags {
      name  = "log_checkpoints"
      value = "off"
    }
    database_flags {
      name  = "log_connections"
      value = "off"
    }
    database_flags {
      name  = "log_disconnections"
      value = "off"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "off"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "99"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "pass2" {
  database_version = "POSTGRES_16"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    ip_configuration {
      require_ssl  = false
      ipv4_enabled = true
      authorized_networks {
        value = "108.12.12.0/24"
        name  = "internal"
      }

      authorized_networks {
        value = "0.0.0.0/0"
        name  = "internet"
      }
    }
    backup_configuration {
      enabled = false
    }
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    database_flags {
      name  = "log_checkpoints"
      value = "off"
    }
    database_flags {
      name  = "log_connections"
      value = "off"
    }
    database_flags {
      name  = "log_disconnections"
      value = "off"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "off"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "99"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "fail3" {
  database_version = "SQLSERVER_2019_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = false
      enabled                        = false
      location                       = "us"
      point_in_time_recovery_enabled = false
      start_time                     = "00:00"
    }

    database_flags {
      name  = "cross db ownership chaining"
      value = "on"
    }
    database_flags {
      name  = "contained database authentication"
      value = "on"
    }


    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = true
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = false
      authorized_networks {
        name  = "theworld"
        value = "0.0.0.0/0"
      }
    }

    location_preference {
      zone = "us-central1-a"
    }

    maintenance_window {
      day  = "1"
      hour = "0"
    }

    pricing_plan = "PER_USE"
    tier         = "db-custom-1-4096"
  }
}

resource "google_sql_database_instance" "pass3" {
  database_version = "SQLSERVER_2022_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = false
      enabled                        = false
      location                       = "us"
      point_in_time_recovery_enabled = false
      start_time                     = "00:00"
    }

    database_flags {
      name  = "cross db ownership chaining"
      value = "on"
    }
    database_flags {
      name  = "contained database authentication"
      value = "on"
    }


    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = true
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = false
      authorized_networks {
        name  = "theworld"
        value = "0.0.0.0/0"
      }
    }

    location_preference {
      zone = "us-central1-a"
    }

    maintenance_window {
      day  = "1"
      hour = "0"
    }

    pricing_plan = "PER_USE"
    tier         = "db-custom-1-4096"
  }
}
