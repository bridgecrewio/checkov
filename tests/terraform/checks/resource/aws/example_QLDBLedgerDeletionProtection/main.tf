# pass

resource "aws_qldb_ledger" "default" {
  name             = "ledger"
  permissions_mode = "STANDARD"
}

resource "aws_qldb_ledger" "enabled" {
  name             = "ledger"
  permissions_mode = "STANDARD"

  deletion_protection = true
}

# failure

resource "aws_qldb_ledger" "disabled" {
  name             = "ledger"
  permissions_mode = "STANDARD"

  deletion_protection = false
}
