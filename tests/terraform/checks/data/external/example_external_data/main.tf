data "external" "external_provider" {
  program = ["python3", "malware.py"]
}

output "external_provider_example" {
  value = data.external.external_provider
}