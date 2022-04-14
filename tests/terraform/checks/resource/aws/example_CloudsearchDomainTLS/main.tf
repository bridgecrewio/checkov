resource "aws_cloudsearch_domain" "fail" {
  name = "example-domain"

  scaling_parameters {
    desired_instance_type = "search.medium"
  }

  index_field {
    name            = "headline"
    type            = "text"
    search          = true
    return          = true
    sort            = true
    highlight       = false
    analysis_scheme = "_en_default_"
  }

  index_field {
    name   = "price"
    type   = "double"
    search = true
    facet  = true
    return = true
    sort   = true
  }
  endpoint_options {
    enforce_https       = false
    tls_security_policy = "Policy-Min-TLS-1-0-2019-07"
  }
}
resource "aws_cloudsearch_domain" "fail2" {
  name = "example-domain"

  scaling_parameters {
    desired_instance_type = "search.medium"
  }

  index_field {
    name            = "headline"
    type            = "text"
    search          = true
    return          = true
    sort            = true
    highlight       = false
    analysis_scheme = "_en_default_"
  }

  index_field {
    name   = "price"
    type   = "double"
    search = true
    facet  = true
    return = true
    sort   = true
  }
  endpoint_options {
    enforce_https = false
  }
}

resource "aws_cloudsearch_domain" "pass" {
  name = "example-domain"

  scaling_parameters {
    desired_instance_type = "search.medium"
  }

  index_field {
    name            = "headline"
    type            = "text"
    search          = true
    return          = true
    sort            = true
    highlight       = false
    analysis_scheme = "_en_default_"
  }

  index_field {
    name   = "price"
    type   = "double"
    search = true
    facet  = true
    return = true
    sort   = true
  }
  endpoint_options {
    enforce_https       = false
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
}
