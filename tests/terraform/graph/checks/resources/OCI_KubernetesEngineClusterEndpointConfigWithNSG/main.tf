resource "oci_containerengine_cluster" "example_cluster" {

  endpoint_config {
    nsg_ids = [
      "ocid1.networksecuritygroup.oc1..example"
    ]
  }
}
