# PASS 1: identity_squash = ROOT, anonymous_gid = 65534 & anonymous_uid = 65534

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

# PASS 2: identity_squash does not contain ROOT, so no validations will run on this snippet.

resource "oci_file_storage_export" "pass_2" {
  export_set_id  = oci_file_storage_export_set.fss_pud_export_set.id
  file_system_id = oci_file_storage_file_system.fss_pud_file_system.id
  path           = var.export_path_fss_pud

  export_options {
    source                         = var.pud_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
  export_options {
    source                         = var.pud_web_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
}

# FAIL 1: identity_squash = ROOT but anonymous_gid & anonymous_uid don't exist

resource "oci_file_storage_export" "fail_1" {
  export_set_id  = oci_file_storage_export_set.fss_pud_export_set.id
  file_system_id = oci_file_storage_file_system.fss_pud_file_system.id
  path           = var.export_path_fss_pud

  export_options {
    source                         = var.pud_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "ROOT"
    require_privileged_source_port = true
  }
  export_options {
    source                         = var.pud_web_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
}

# FAIL 2: identity_squash = ROOT but anonymous_gid & anonymous_uid NOT equals to 65534

resource "oci_file_storage_export" "fail_2" {
  export_set_id  = oci_file_storage_export_set.fss_pud_export_set.id
  file_system_id = oci_file_storage_file_system.fss_pud_file_system.id
  path           = var.export_path_fss_pud

  export_options {
    source                         = var.pud_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "NONE"
    require_privileged_source_port = true
  }
  export_options {
    source                         = var.pud_web_subnet_cidr_block
    access                         = "READ_WRITE"
    identity_squash                = "ROOT"
    anonymous_gid = 0
    anonymous_uid = 4294967295
    require_privileged_source_port = true
  }
}