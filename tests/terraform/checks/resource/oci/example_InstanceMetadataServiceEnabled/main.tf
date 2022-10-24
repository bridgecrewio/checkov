resource "oci_core_instance" "fail" {
  availability_domain = var.instance_availability_domain
  compartment_id      = var.compartment_id
  shape               = var.instance_shape

  create_vnic_details {
    assign_private_dns_record = var.instance_create_vnic_details_assign_private_dns_record
    assign_public_ip          = var.instance_create_vnic_details_assign_public_ip
    defined_tags              = { "Operations.CostCenter" = "42" }
    display_name              = var.instance_create_vnic_details_display_name
    freeform_tags             = { "Department" = "Finance" }
    hostname_label            = var.instance_create_vnic_details_hostname_label
    nsg_ids                   = var.instance_create_vnic_details_nsg_ids
    private_ip                = var.instance_create_vnic_details_private_ip
    skip_source_dest_check    = var.instance_create_vnic_details_skip_source_dest_check
    subnet_id                 = oci_core_subnet.test_subnet.id
    vlan_id                   = oci_core_vlan.test_vlan.id
  }

  dedicated_vm_host_id = oci_core_dedicated_vm_host.test_dedicated_vm_host.id
  defined_tags         = { "Operations.CostCenter" = "42" }
  display_name         = var.instance_display_name
  extended_metadata = {
    some_string   = "stringA"
    nested_object = "{\"some_string\": \"stringB\", \"object\": {\"some_string\": \"stringC\"}}"
  }

  fault_domain  = var.instance_fault_domain
  freeform_tags = { "Department" = "Finance" }

  instance_options {
    are_legacy_imds_endpoints_disabled = false
  }

  ipxe_script                         = var.instance_ipxe_script
  is_pv_encryption_in_transit_enabled = var.instance_is_pv_encryption_in_transit_enabled

  launch_options {
    boot_volume_type                    = var.instance_launch_options_boot_volume_type
    firmware                            = var.instance_launch_options_firmware
    is_consistent_volume_naming_enabled = var.instance_launch_options_is_consistent_volume_naming_enabled
    network_type                        = var.instance_launch_options_network_type
    remote_data_volume_type             = var.instance_launch_options_remote_data_volume_type
  }

  metadata = var.instance_metadata

  platform_config {
    type                               = var.instance_platform_config_type
    is_measured_boot_enabled           = var.instance_platform_config_is_measured_boot_enabled
    is_secure_boot_enabled             = var.instance_platform_config_is_secure_boot_enabled
    is_trusted_platform_module_enabled = var.instance_platform_config_is_trusted_platform_module_enabled
    numa_nodes_per_socket              = var.instance_platform_config_numa_nodes_per_socket
  }

  preemptible_instance_config {
    preemption_action {
      type                 = var.instance_preemptible_instance_config_preemption_action_type
      preserve_boot_volume = var.instance_preemptible_instance_config_preemption_action_preserve_boot_volume
    }
  }
  shape_config {
    baseline_ocpu_utilization = var.instance_shape_config_baseline_ocpu_utilization
    memory_in_gbs             = var.instance_shape_config_memory_in_gbs
    ocpus                     = var.instance_shape_config_ocpus
  }
  source_details {
    source_id               = oci_core_image.test_image.id
    source_type             = "image"
    boot_volume_size_in_gbs = var.instance_source_details_boot_volume_size_in_gbs
  }
  preserve_boot_volume = false
}

resource "oci_core_instance" "pass" {
  availability_domain = var.instance_availability_domain
  compartment_id      = var.compartment_id
  shape               = var.instance_shape

  agent_config {
    is_pv_encryption_in_transit_enabled = True
    are_all_plugins_disabled            = var.instance_agent_config_are_all_plugins_disabled
    is_management_disabled              = var.instance_agent_config_is_management_disabled
    is_monitoring_disabled              = var.instance_agent_config_is_monitoring_disabled

    plugins_config {
      desired_state = var.instance_agent_config_plugins_config_desired_state
      name          = var.instance_agent_config_plugins_config_name
    }
  }

  availability_config {
    is_live_migration_preferred = var.instance_availability_config_is_live_migration_preferred
    recovery_action             = var.instance_availability_config_recovery_action
  }

  create_vnic_details {
    assign_private_dns_record = var.instance_create_vnic_details_assign_private_dns_record
    assign_public_ip          = var.instance_create_vnic_details_assign_public_ip
    defined_tags              = { "Operations.CostCenter" = "42" }
    display_name              = var.instance_create_vnic_details_display_name
    freeform_tags             = { "Department" = "Finance" }
    hostname_label            = var.instance_create_vnic_details_hostname_label
    nsg_ids                   = var.instance_create_vnic_details_nsg_ids
    private_ip                = var.instance_create_vnic_details_private_ip
    skip_source_dest_check    = var.instance_create_vnic_details_skip_source_dest_check
    subnet_id                 = oci_core_subnet.test_subnet.id
    vlan_id                   = oci_core_vlan.test_vlan.id
  }

  dedicated_vm_host_id = oci_core_dedicated_vm_host.test_dedicated_vm_host.id
  defined_tags         = { "Operations.CostCenter" = "42" }
  display_name         = var.instance_display_name

  extended_metadata = {
    some_string   = "stringA"
    nested_object = "{\"some_string\": \"stringB\", \"object\": {\"some_string\": \"stringC\"}}"
  }

  fault_domain  = var.instance_fault_domain
  freeform_tags = { "Department" = "Finance" }

  instance_options {
    are_legacy_imds_endpoints_disabled = true
  }

  ipxe_script                         = var.instance_ipxe_script
  is_pv_encryption_in_transit_enabled = var.instance_is_pv_encryption_in_transit_enabled

  launch_options {
    boot_volume_type                    = var.instance_launch_options_boot_volume_type
    firmware                            = var.instance_launch_options_firmware
    is_consistent_volume_naming_enabled = var.instance_launch_options_is_consistent_volume_naming_enabled
    is_pv_encryption_in_transit_enabled = true
    network_type                        = var.instance_launch_options_network_type
    remote_data_volume_type             = var.instance_launch_options_remote_data_volume_type
  }

  metadata = var.instance_metadata
  platform_config {
    type                               = var.instance_platform_config_type
    is_measured_boot_enabled           = var.instance_platform_config_is_measured_boot_enabled
    is_secure_boot_enabled             = var.instance_platform_config_is_secure_boot_enabled
    is_trusted_platform_module_enabled = var.instance_platform_config_is_trusted_platform_module_enabled
    numa_nodes_per_socket              = var.instance_platform_config_numa_nodes_per_socket
  }

  preemptible_instance_config {
    preemption_action {
      type                 = var.instance_preemptible_instance_config_preemption_action_type
      preserve_boot_volume = var.instance_preemptible_instance_config_preemption_action_preserve_boot_volume
    }
  }

  shape_config {
    baseline_ocpu_utilization = var.instance_shape_config_baseline_ocpu_utilization
    memory_in_gbs             = var.instance_shape_config_memory_in_gbs
    ocpus                     = var.instance_shape_config_ocpus
  }

  source_details {
    source_id               = oci_core_image.test_image.id
    source_type             = "image"
    boot_volume_size_in_gbs = var.instance_source_details_boot_volume_size_in_gbs
  }

  preserve_boot_volume = false
}

resource "oci_core_instance" "fail2" {
  availability_domain = var.instance_availability_domain
  compartment_id      = var.compartment_id
  shape               = var.instance_shape

  agent_config {
    is_pv_encryption_in_transit_enabled = True
    are_all_plugins_disabled            = var.instance_agent_config_are_all_plugins_disabled
    is_management_disabled              = var.instance_agent_config_is_management_disabled
    is_monitoring_disabled              = var.instance_agent_config_is_monitoring_disabled

    plugins_config {
      desired_state = var.instance_agent_config_plugins_config_desired_state
      name          = var.instance_agent_config_plugins_config_name
    }
  }

  availability_config {
    is_live_migration_preferred = var.instance_availability_config_is_live_migration_preferred
    recovery_action             = var.instance_availability_config_recovery_action
  }

  create_vnic_details {
    assign_private_dns_record = var.instance_create_vnic_details_assign_private_dns_record
    assign_public_ip          = var.instance_create_vnic_details_assign_public_ip
    defined_tags              = { "Operations.CostCenter" = "42" }
    display_name              = var.instance_create_vnic_details_display_name
    freeform_tags             = { "Department" = "Finance" }
    hostname_label            = var.instance_create_vnic_details_hostname_label
    nsg_ids                   = var.instance_create_vnic_details_nsg_ids
    private_ip                = var.instance_create_vnic_details_private_ip
    skip_source_dest_check    = var.instance_create_vnic_details_skip_source_dest_check
    subnet_id                 = oci_core_subnet.test_subnet.id
    vlan_id                   = oci_core_vlan.test_vlan.id
  }

  dedicated_vm_host_id = oci_core_dedicated_vm_host.test_dedicated_vm_host.id
  defined_tags         = { "Operations.CostCenter" = "42" }
  display_name         = var.instance_display_name

  extended_metadata = {
    some_string   = "stringA"
    nested_object = "{\"some_string\": \"stringB\", \"object\": {\"some_string\": \"stringC\"}}"
  }

  fault_domain  = var.instance_fault_domain
  freeform_tags = { "Department" = "Finance" }

  ipxe_script                         = var.instance_ipxe_script
  is_pv_encryption_in_transit_enabled = var.instance_is_pv_encryption_in_transit_enabled

  launch_options {
    boot_volume_type                    = var.instance_launch_options_boot_volume_type
    firmware                            = var.instance_launch_options_firmware
    is_consistent_volume_naming_enabled = var.instance_launch_options_is_consistent_volume_naming_enabled
    is_pv_encryption_in_transit_enabled = true
    network_type                        = var.instance_launch_options_network_type
    remote_data_volume_type             = var.instance_launch_options_remote_data_volume_type
  }

  metadata = var.instance_metadata
  platform_config {
    type                               = var.instance_platform_config_type
    is_measured_boot_enabled           = var.instance_platform_config_is_measured_boot_enabled
    is_secure_boot_enabled             = var.instance_platform_config_is_secure_boot_enabled
    is_trusted_platform_module_enabled = var.instance_platform_config_is_trusted_platform_module_enabled
    numa_nodes_per_socket              = var.instance_platform_config_numa_nodes_per_socket
  }

  preemptible_instance_config {
    preemption_action {
      type                 = var.instance_preemptible_instance_config_preemption_action_type
      preserve_boot_volume = var.instance_preemptible_instance_config_preemption_action_preserve_boot_volume
    }
  }

  shape_config {
    baseline_ocpu_utilization = var.instance_shape_config_baseline_ocpu_utilization
    memory_in_gbs             = var.instance_shape_config_memory_in_gbs
    ocpus                     = var.instance_shape_config_ocpus
  }

  source_details {
    source_id               = oci_core_image.test_image.id
    source_type             = "image"
    boot_volume_size_in_gbs = var.instance_source_details_boot_volume_size_in_gbs
  }

  preserve_boot_volume = false
}