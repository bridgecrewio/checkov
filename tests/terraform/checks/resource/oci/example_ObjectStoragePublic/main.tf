resource "oci_objectstorage_bucket" "pass" {
  compartment_id = var.compartment_id
  name           = var.bucket_name
  namespace      = var.namespace

  #access_type           = var.bucket_access_type
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  kms_key_id            = var.oci_kms_key.id
  metadata              = var.metadata
  storage_tier          = var.bucket_storage_tier
  object_events_enabled = true

  retention_rules {
    display_name = var.retention_rule_display_name

    duration {
      time_amount = var.retention_rule_duration_time_amount
      time_unit   = var.retention_rule_duration_time_unit
    }
    time_rule_locked = var.retention_rule_time_rule_locked
  }

  versioning = true
}

resource "oci_objectstorage_bucket" "pass2" {
  compartment_id = var.compartment_id
  name           = var.bucket_name
  namespace      = var.namespace

  access_type           = "NoPublicAccess"
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  kms_key_id            = var.oci_kms_key.id
  metadata              = var.metadata
  storage_tier          = var.bucket_storage_tier
  object_events_enabled = true

  retention_rules {
    display_name = var.retention_rule_display_name

    duration {
      time_amount = var.retention_rule_duration_time_amount
      time_unit   = var.retention_rule_duration_time_unit
    }
    time_rule_locked = var.retention_rule_time_rule_locked
  }

  versioning = true
}

resource "oci_objectstorage_bucket" "fail" {
  compartment_id = var.compartment_id
  name           = var.bucket_name
  namespace      = var.namespace

  access_type           = "ObjectReadWithoutList"
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  metadata              = var.metadata
  storage_tier          = var.bucket_storage_tier
  object_events_enabled = false

  retention_rules {
    display_name = var.retention_rule_display_name

    duration {
      time_amount = var.retention_rule_duration_time_amount
      time_unit   = var.retention_rule_duration_time_unit
    }
    time_rule_locked = var.retention_rule_time_rule_locked
  }

  versioning = false
}


resource "oci_objectstorage_bucket" "fail2" {
  compartment_id = var.compartment_id
  name           = var.bucket_name
  namespace      = var.namespace

  access_type           = "ObjectRead"
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  metadata              = var.metadata
  storage_tier          = var.bucket_storage_tier
  object_events_enabled = false

  retention_rules {
    display_name = var.retention_rule_display_name

    duration {
      time_amount = var.retention_rule_duration_time_amount
      time_unit   = var.retention_rule_duration_time_unit
    }
    time_rule_locked = var.retention_rule_time_rule_locked
  }

  versioning = false
}