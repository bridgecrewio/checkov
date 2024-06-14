# pass
resource "tencentcloud_instance" "positive1" {
  instance_name     = "cvm_postpaid"
  availability_zone = data.tencentcloud_availability_zones.my_favorite_zones.zones.0.name
  image_id          = data.tencentcloud_images.my_favorite_image.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.my_favorite_instance_types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50
}

resource "tencentcloud_instance" "positive2" {
  instance_name     = "cvm_postpaid"
  availability_zone = data.tencentcloud_availability_zones.my_favorite_zones.zones.0.name
  image_id          = data.tencentcloud_images.my_favorite_image.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.my_favorite_instance_types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50

  user_data = base64encode("this is test value")
}

resource "tencentcloud_instance" "positive3" {
  instance_name     = "cvm_postpaid"
  availability_zone = data.tencentcloud_availability_zones.my_favorite_zones.zones.0.name
  image_id          = data.tencentcloud_images.my_favorite_image.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.my_favorite_instance_types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50

  user_data_raw = "this is test value"
}


# failed
resource "tencentcloud_instance" "negative1" {
  instance_name     = "cvm_postpaid"
  availability_zone = data.tencentcloud_availability_zones.my_favorite_zones.zones.0.name
  image_id          = data.tencentcloud_images.my_favorite_image.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.my_favorite_instance_types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50

  user_data = base64encode("apt-get install -y tccli; export TENCENTCLOUD_SECRET_ID=your_access_key_id_here; export TENCENTCLOUD_SECRET_KEY=your_secret_access_key_here")

}

resource "tencentcloud_instance" "negative2" {
  instance_name     = "cvm_postpaid"
  availability_zone = data.tencentcloud_availability_zones.my_favorite_zones.zones.0.name
  image_id          = data.tencentcloud_images.my_favorite_image.images.0.image_id
  instance_type     = data.tencentcloud_instance_types.my_favorite_instance_types.instance_types.0.instance_type
  system_disk_type  = "CLOUD_PREMIUM"
  system_disk_size  = 50

  user_data_raw = "apt-get install -y tccli; export TENCENTCLOUD_SECRET_ID=your_access_key_id_here; export TENCENTCLOUD_SECRET_KEY=your_secret_access_key_here"

}