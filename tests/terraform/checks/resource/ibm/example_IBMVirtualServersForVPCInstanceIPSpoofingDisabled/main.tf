resource "ibm_is_instance" "fail_1" {
  name    = "example-instance-reserved-ip"
  image   = data.id
  profile = "bc1-2x8"

  primary_network_interface {
    name   = "eth0"
    subnet = data.subnet
    primary_ip {
      reserved_ip = data.res_ip
    }
    allow_ip_spoofing = false
  }
  network_interfaces {
    name              = "eth1"
    subnet            = data.ibm_is_subnet
    allow_ip_spoofing = true
    primary_ip {
      name        = "example-reserved-ip1"
      auto_delete = true
      address     = data.address
    }
  }
}

resource "ibm_is_instance" "fail_2" {
  name    = "example-instance-reserved-ip"
  image   = data.id
  profile = "bc1-2x8"

  primary_network_interface {
    name   = "eth0"
    subnet = data.subnet
    primary_ip {
      reserved_ip = data.res_ip
    }
    allow_ip_spoofing = true
  }
  network_interfaces {
    name              = "eth1"
    subnet            = data.ibm_is_subnet
    allow_ip_spoofing = false
    primary_ip {
      name        = "example-reserved-ip1"
      auto_delete = true
      address     = data.address
    }
  }
}

resource "ibm_is_instance" "fail_3" {
  name    = "example-instance-reserved-ip"
  image   = data.id
  profile = "bc1-2x8"

  primary_network_interface {
    name   = "eth0"
    subnet = data.subnet
    primary_ip {
      reserved_ip = data.res_ip
    }
  }
  network_interfaces {
    name              = "eth1"
    subnet            = data.ibm_is_subnet
    allow_ip_spoofing = true
    primary_ip {
      name        = "example-reserved-ip1"
      auto_delete = true
      address     = data.address
    }
  }
}

resource "ibm_is_instance" "pass_1" {
  name    = "example-instance-reserved-ip"
  image   = data.id
  profile = "bc1-2x8"

  primary_network_interface {
    name   = "eth0"
    subnet = data.subnet
    primary_ip {
      reserved_ip = data.res_ip
    }
  }
  network_interfaces {
    name   = "eth1"
    subnet = data.ibm_is_subnet
    primary_ip {
      name        = "example-reserved-ip1"
      auto_delete = true
      address     = data.address
    }
  }
}

resource "ibm_is_instance" "pass_2" {
  name    = "example-instance-reserved-ip"
  image   = ibm_is_image.example.id
  profile = "bc1-2x8"

  primary_network_interface {
    name   = "eth0"
    subnet = data.ibm_is_subnet.pike.id
    primary_ip {
      reserved_ip = data.ibm_is_subnet_reserved_ip.pike.id
    }
    allow_ip_spoofing = false
  }
}

resource "ibm_is_image" "example" {
  name               = "example-image"
  href               = "cos://us-south/buckettesttest/livecd.ubuntu-cpc.azure.vhd"
  operating_system   = "ubuntu-16-04-amd64"
  encrypted_data_key = "eJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0="
  encryption_key     = "crn:v1:bluemix:public:kms:us-south:a/6xxxxxxxxxxxxxxx:xxxxxxx-xxxx-xxxx-xxxxxxx:key:dxxxxxx-fxxx-4xxx-9xxx-7xxxxxxxx"
}

data "ibm_is_subnet_reserved_ip" "pike" {
  subnet      = data.ibm_is_subnet.pike.id
  reserved_ip = "127.0.0.1"
}

data "ibm_is_subnet" "pike" {
  identifier = "someshizzle"
}

provider "ibm" {}
