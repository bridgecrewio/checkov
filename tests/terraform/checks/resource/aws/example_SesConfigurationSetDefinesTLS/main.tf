resource "aws_ses_configuration_set" "fail" {
  name = "some-configuration-set-test"
}

resource "aws_ses_configuration_set" "pass" {
  name = "some-configuration-set-test"

  delivery_options {
    tls_policy = "Require"
  }
}

resource "aws_ses_configuration_set" "fail2" {
  name = "some-configuration-set-test"

  delivery_options {
    tls_policy = "Optional"
  }
}