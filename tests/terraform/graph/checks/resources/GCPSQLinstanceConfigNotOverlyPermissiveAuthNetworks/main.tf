# Pass case 1: No authorised networks set

resource "google_sql_database_instance" "pass_1" {
  name             = "sqldbi"
  database_version = "SQLSERVER_2017_STANDARD"
  region           = "us-central1"


  deletion_protection = false
  settings {
    # Second-generation instance tiers are based on the machine
    # type. See argument reference below.
    tier = "db-custom-2-5120"
    }
      root_password = "pud123"
}


# Pass case 2- Authorised n/w not overly permissive 

resource "google_sql_database_instance" "pass_2" {
  name             = "sqldbi"
  database_version = "SQLSERVER_2017_STANDARD"
  deletion_protection = false
  depends_on       = [google_service_networking_connection.dep-vpc-j3-1-rlp-87327]
  settings {
    tier              = "db-custom-2-5120"
    availability_type = "REGIONAL"
    disk_size         = 10  # 10 GB is the smallest disk size
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.dep-vpc-j1-2-rlp-87327.self_link
      authorized_networks {
        value           = "101.0.0.0/16"
        name            = "first"
        expiration_time = "2023-11-15T16:19:00.094Z"
      }
    }
  }
  root_password = "pud123"
}



# FAIL case 1 - overly permissive IPV4 authorised n/w (0.0.0.0)

resource "google_sql_database_instance" "fail_1" {
  name             = "sqldbi"
  database_version = "SQLSERVER_2017_STANDARD"
  region           = "us-central1"


  deletion_protection = false
  settings {
    tier = "db-custom-2-5120"
    ip_configuration {
      authorized_networks {
        value = "0.0.0.0/0"
      }
    }
  }
  root_password = "pud123"
}

# FAIL case 2: overly permissive IPV6 authorised n/w (::/0)
resource "google_sql_database_instance" "fail_2" {
  name             = "sqldbi"
  database_version = "SQLSERVER_2017_STANDARD"
  region           = "us-central1"


  deletion_protection = false
  settings {
    # Second-generation instance tiers are based on the machine
    # type. See argument reference below.
    tier = "db-custom-2-5120"
    ip_configuration {
      authorized_networks {
        value = "::/0"
      }
    }
  }
  root_password = "pud123"
}


