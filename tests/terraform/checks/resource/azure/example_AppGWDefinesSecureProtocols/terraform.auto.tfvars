ssl_policy = {
  disabled_protocols = []
  policy_type        = "Custom"
  cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
  ]
  min_protocol_version = "TLSv1_2"
}