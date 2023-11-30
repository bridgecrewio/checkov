# Case 1: Pass, 'private_service_endpoint' is 'true'

resource "ibm_container_cluster" "pass_1" {
  name            = "pud_pass_1"
  gateway_enabled = true
  datacenter      = "dal10"
  machine_type    = "b3c.4x16"
  hardware        = "shared"
  private_vlan_id = "2709721"
  private_service_endpoint = true
}

# Case 2: Pass, public_service_endpoint is false

resource "ibm_container_cluster" "pass_2" {
  name            = "pud_pass_2"
  gateway_enabled = true
  datacenter      = "dal10"
  machine_type    = "b3c.4x16"
  hardware        = "shared"
  private_vlan_id = "2709721"
  private_service_endpoint = true
  public_service_endpoint = false
}

# Case 3: Fail, "private_service_endpoint" is not true

resource "ibm_container_cluster" "fail_1" {
  name            = "pud_fail_1"
  gateway_enabled = true
  datacenter      = "dal10"
  machine_type    = "b3c.4x16"
  hardware        = "shared"
  private_vlan_id = "2709721"
  private_service_endpoint = false
}

# Case 4: Fail, public_service_endpoint and private_service_endpoint is true

resource "ibm_container_cluster" "fail_2" {
  name            = "pud_fail_2"
  gateway_enabled = true
  datacenter      = "dal10"
  machine_type    = "b3c.4x16"
  hardware        = "shared"
  private_vlan_id = "2709721"
  private_service_endpoint = true
  public_service_endpoint = true
}

# Case 5: Fail, private_service_endpoint does not exist, defaulting to public accessibility

resource "ibm_container_cluster" "fail_3" {
  name            = "pud_fail_3"
  gateway_enabled = true
  datacenter      = "dal10"
  machine_type    = "b3c.4x16"
  hardware        = "shared"
  private_vlan_id = "2709721"
}