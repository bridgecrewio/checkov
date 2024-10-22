# Case 1: Pass, allow list contains a valid IP range

resource "ibm_database" "pass" {
  name                         = "pud_mysql_db_pass_1"
  service                      = "databases-for-mysql"
  plan                         = "platinum"
  location                     = "eu-gb"

  allowlist {
    address     = "172.168.1.2/16"
    description = "desc1"
  }
}

# Case 2: Fail, allow list contains a invalid IP range - 0.0.0.0/0

resource "ibm_database" "fail_1" {
  name                         = "pud_mysql_db_pass_1"
  service                      = "databases-for-mysql"
  plan                         = "platinum"
  location                     = "eu-gb"

  allowlist {
    address     = "0.0.0.0/0"
    description = "desc1"
  }
}

# Case 3: Fail, allow list does NOT contain IP range, defaults to 0.0.0.0/0

resource "ibm_database" "fail_2" {
  name                         = "pud_mysql_db_pass_1"
  service                      = "databases-for-mysql"
  plan                         = "platinum"
  location                     = "eu-gb"
}