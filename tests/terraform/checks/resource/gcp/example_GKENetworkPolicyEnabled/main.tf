# PASS: legacy network policy is explicitly enabled.
resource "google_container_cluster" "network_policy_enabled" {
  name               = "network-policy-enabled"
  location           = "us-central1"
  initial_node_count = 1

  network_policy {
    enabled = true
  }
}

# PASS: Dataplane V2 enforces Kubernetes NetworkPolicy without the legacy block.
resource "google_container_cluster" "advanced_datapath_without_network_policy" {
  name               = "advanced-datapath-no-network-policy"
  location           = "us-central1"
  initial_node_count = 1
  datapath_provider  = "ADVANCED_DATAPATH"
}

# PASS: Dataplane V2 remains compliant when the legacy block is explicitly disabled.
resource "google_container_cluster" "advanced_datapath_with_network_policy_disabled" {
  name               = "advanced-datapath-network-policy-disabled"
  location           = "us-central1"
  initial_node_count = 1
  datapath_provider  = "ADVANCED_DATAPATH"

  network_policy {
    enabled = false
  }
}

# PASS: dedicated Autopilot clusters enforce network policy through Dataplane V2.
resource "google_container_cluster" "autopilot" {
  name             = "autopilot-network-policy"
  location         = "us-central1"
  enable_autopilot = true
}

# FAIL: legacy network policy is explicitly disabled and Dataplane V2 is not enabled.
resource "google_container_cluster" "network_policy_disabled" {
  name               = "network-policy-disabled"
  location           = "us-central1"
  initial_node_count = 1

  network_policy {
    enabled = false
  }
}

# FAIL: Standard cluster omits every supported network-policy enforcement signal.
resource "google_container_cluster" "network_policy_omitted" {
  name               = "network-policy-omitted"
  location           = "us-central1"
  initial_node_count = 1
}

# FAIL: explicitly disabling Autopilot does not establish network-policy enforcement.
resource "google_container_cluster" "autopilot_disabled" {
  name               = "autopilot-disabled"
  location           = "us-central1"
  initial_node_count = 1
  enable_autopilot   = false
}
