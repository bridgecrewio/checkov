resource "ncloud_nks_cluster" "pass" {
  cluster_type                = "SVR.VNKS.STAND.C002.M008.NET.SSD.B050.G002"
  k8s_version                 = data.ncloud_nks_versions.version.versions.0.value
  login_key_name              = ncloud_login_key.loginkey.key_name
  name                        = "sample-cluster"
  lb_private_subnet_no        = ncloud_subnet.subnet_lb.id
  kube_network_plugin         = "cilium"
  subnet_no_list              = [ ncloud_subnet.subnet.id ]
  vpc_no                      = ncloud_vpc.vpc.id
  zone                        = "KR-1"
  public_network = false
  log {
    audit = true
  }
}
resource "ncloud_nks_cluster" "fail" {
  cluster_type                = "SVR.VNKS.STAND.C002.M008.NET.SSD.B050.G002"
  k8s_version                 = data.ncloud_nks_versions.version.versions.0.value
  login_key_name              = ncloud_login_key.loginkey.key_name
  name                        = "sample-cluster"
  lb_private_subnet_no        = ncloud_subnet.subnet_lb.id
  kube_network_plugin         = "cilium"
  subnet_no_list              = [ ncloud_subnet.subnet.id ]
  vpc_no                      = ncloud_vpc.vpc.id
  zone                        = "KR-1"
  public_network = false
  log {
    audit = false
  }
}
resource "ncloud_nks_cluster" "fail2" {
  cluster_type                = "SVR.VNKS.STAND.C002.M008.NET.SSD.B050.G002"
  k8s_version                 = data.ncloud_nks_versions.version.versions.0.value
  login_key_name              = ncloud_login_key.loginkey.key_name
  name                        = "sample-cluster"
  lb_private_subnet_no        = ncloud_subnet.subnet_lb.id
  kube_network_plugin         = "cilium"
  subnet_no_list              = [ ncloud_subnet.subnet.id ]
  vpc_no                      = ncloud_vpc.vpc.id
  zone                        = "KR-1"
  public_network = false
}
