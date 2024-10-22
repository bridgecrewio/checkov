
resource "google_sql_database_instance" "fail" {
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "false"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "false"
      start_time                     = "00:00"
    }


    database_flags {
      name  = "cross db ownership chaining"
      value = "on"
    }

    database_flags {
      name  = "contained database authentication"
      value = "off"
    }

    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = "false"
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = "false"
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
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "false"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "false"
      start_time                     = "00:00"
    }

    database_flags {
      name  = "cross db ownership chaining"
      value = "off"
    }

    database_flags {
      name  = "contained database authentication"
      value = "off"
    }

    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = "false"
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = "false"
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


resource "google_sql_database_instance" "pass2" {
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "false"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "false"
      start_time                     = "00:00"
    }

    database_flags {
      name  = "contained database authentication"
      value = "off"
    }

    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = "false"
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = "false"
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


resource "google_sql_database_instance" "pass" {
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    tier = "db-custom-1-4096"
  }
}

resource "google_sql_database_instance" "unknown" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_checkpoints"
      value = "off"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "unknown_var" {
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
   database_flags = ["${var.test_var}"]
    tier = "db-custom-1-4096"
  }
}