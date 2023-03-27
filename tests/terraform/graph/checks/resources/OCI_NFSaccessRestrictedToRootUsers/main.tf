resource "oci_file_storage_export" "pass_1" {

  export_options {
    protocol = "NFS"
    access = "READ_WRITE"
    identity_squash = "NONE"
    anonymous_gid = 65534
    anonymous_uid = 65534
  }

  export_options {
    protocol = "NFS"
    access = "READ_WRITE"
    identity_squash = "root"
    anonymous_gid = 65534
    anonymous_uid = 65534
    
  }

}


resource "oci_file_storage_export" "fail_1" {
  export_set_id  = oci_file_storage_export_set.fss_sap_export_set.id
  file_system_id = oci_file_storage_file_system.fss_sap_file_system.id
  path           = var.export_path_fss_sap

  export_options {
    source                         = var.sap_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
  export_options {
    source                         = var.sap_web_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
  export_options {
    source                         = var.database_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
}