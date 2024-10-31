resource "aws_transfer_server" "fail_old" {
  endpoint_type = "PUBLIC"
  identity_provider_type = "SERVICE_MANAGED"

  # Using an outdated security policy (not the latest)
  security_policy_name = "TransferSecurityPolicy-2018-11"

  tags = {
    Name = "OldTransferServer"
  }
}

resource "aws_transfer_server" "pass_new" {
  endpoint_type = "PUBLIC"
  identity_provider_type = "SERVICE_MANAGED"

  # Using the latest security policy (as of this example)
  security_policy_name = "TransferSecurityPolicy-2024-01"

  tags = {
    Name = "LatestTransferServer"
  }
}

resource "aws_transfer_server" "fail_old_fips" {
  endpoint_type = "PUBLIC"
  identity_provider_type = "SERVICE_MANAGED"

  # Using the latest security policy (as of this example)
  security_policy_name = "TransferSecurityPolicy-FIPS-2020-06"

  tags = {
    Name = "LatestTransferServer"
  }
}

resource "aws_transfer_server" "pass_fips" {
  endpoint_type = "PUBLIC"
  identity_provider_type = "SERVICE_MANAGED"

  # Using the latest security policy (as of this example)
  security_policy_name = "TransferSecurityPolicy-FIPS-2024-01"

  tags = {
    Name = "LatestTransferServer"
  }
}
