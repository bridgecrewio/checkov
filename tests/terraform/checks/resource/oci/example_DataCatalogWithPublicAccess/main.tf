terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 4.0"
    }
  }
}

provider "oci" {
  # Configure the OCI provider here
  # You need to specify tenancy_ocid, user_ocid, fingerprint, and private_key_path
  region = "us-ashburn-1"
}

resource "oci_identity_compartment" "example_compartment" {
  name           = "example-compartment"
  description    = "Compartment for Data Catalog example"
  compartment_id = var.tenancy_ocid
}

resource "oci_datacatalog_catalog" "fail1" {
  compartment_id = oci_identity_compartment.example_compartment.id
  display_name   = "example-catalog"

  # This configuration fails the policy
  attached_catalog_private_endpoints = []

  # Ensure the catalog is in ACTIVE state
  lifecycle {
    ignore_changes = [
      # Ignore changes to tags, as they are often changed outside of Terraform
      defined_tags, freeform_tags,
    ]
  }
}

resource "oci_datacatalog_catalog" "fail2" {
  compartment_id = oci_identity_compartment.example_compartment.id
  display_name   = "example-catalog"

  # Ensure the catalog is in ACTIVE state
  lifecycle {
    ignore_changes = [
      # Ignore changes to tags, as they are often changed outside of Terraform
      defined_tags, freeform_tags,
    ]
  }
}

resource "oci_datacatalog_catalog_private_endpoint" "example_private_endpoint" {
  compartment_id = oci_identity_compartment.example_compartment.id
  dns_zones      = ["example.oraclecloud.com"]
  subnet_id      = "ocid1.subnet.oc1..example"  # Replace with actual subnet OCID
  display_name   = "example-private-endpoint"
}

resource "oci_datacatalog_catalog" "pass" {
  compartment_id = oci_identity_compartment.example_compartment.id
  display_name   = "example-catalog"

  attached_catalog_private_endpoints = [oci_datacatalog_catalog_private_endpoint.example_private_endpoint.id]

  # Ensure the catalog is in ACTIVE state
  lifecycle {
    ignore_changes = [
      # Ignore changes to tags, as they are often changed outside of Terraform
      defined_tags, freeform_tags,
    ]
  }
}

# Output to verify the lifecycle state
output "catalog_lifecycle_state" {
  value = oci_datacatalog_catalog.example_catalog.lifecycle_state
}