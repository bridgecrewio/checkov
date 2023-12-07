#Case 1:

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

#Case 2: FAIL
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

#Case 3: FAIL
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

#Case 4: PASS
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
    name              = "eth1"
    subnet            = data.ibm_is_subnet
    primary_ip {
      name        = "example-reserved-ip1"
      auto_delete = true
      address     = data.address
    }
  }
}


#Case 5:

resource "ibm_is_instance" "pass_2" {
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
}
