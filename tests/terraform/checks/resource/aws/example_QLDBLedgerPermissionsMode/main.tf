# pass

resource "aws_qldb_ledger" "standard" {
  name             = "ledger"
  permissions_mode = "STANDARD"
}

# failure

resource "aws_qldb_ledger" "allow_all" {
  name             = "ledger"
  permissions_mode = "ALLOW_ALL"
}
