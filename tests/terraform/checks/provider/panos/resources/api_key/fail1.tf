provider "panos" {
  api_key = var.nested_var.base64_enc_apikey
}
