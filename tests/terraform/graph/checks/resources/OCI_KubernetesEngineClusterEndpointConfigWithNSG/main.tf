resource "oci_containerengine_cluster" "pass_1" {

  endpoint_config {
    nsg_ids = [
      "ocid1.networksecuritygroup.oc1..pud_cki_1",
      "ocid2.networksecuritygroup.oc1..pud_cki_2",
    ]
  }
}

resource "oci_containerengine_cluster" "fail_1" {

  endpoint_config {
    nsg_ids = "null"
  }
}

resource "oci_containerengine_cluster" "fail_2" {

  endpoint_config {
    nsg_ids = []
  }
}

