resource "ncloud_nas_volume" "pass" {
    volume_name_postfix = "vol"
    volume_size = "600"
    volume_allotment_protocol_type = "NFS"
    is_encrypted_volume = true
}

resource "ncloud_nas_volume" "fail" {
    volume_name_postfix = "vol"
    volume_size = "600"
    volume_allotment_protocol_type = "NFS"
}

resource "ncloud_nas_volume" "fail2" {
    volume_name_postfix = "vol"
    volume_size = "600"
    volume_allotment_protocol_type = "NFS"
    is_encrypted_volume = false
}