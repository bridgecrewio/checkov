from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class K8sEnableNetworkPolicies(BaseResourceCheck):
    def __init__(self):
        """
        Kubernetes Cluster should have Terway or Flannel as CNI Network Plugin as it allows you to use
        standard Kubernetes network policies
        https://www.alibabacloud.com/help/en/container-service-for-kubernetes/latest/work-with-terway
        https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/cs_kubernetes#cluster_network_type
        The vswitches for the pod network when using Terway.Be careful the pod_vswitch_ids can not equal to
        worker_vswitch_ids or master_vswitch_ids but must be in same availability zones.
        Flannel requires pod_cidr.
        """

        name = "Ensure Kubernetes installs plugin Terway or Flannel to support standard policies"
        id = "CKV_ALI_26"
        supported_resources = ['alicloud_cs_kubernetes']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # required fields
        if not (conf.get("pod_vswitch_ids") or conf.get("pod_cidr")):
            return CheckResult.FAILED
        # addons
        if conf.get("addons") and isinstance(conf.get("addons"), list):
            names = [
                addon["name"][0]
                for addon in conf["addons"]
                if addon.get("name")
            ]

            if "terway-eniip" in names:
                if conf.get("pod_vswitch_ids") and isinstance(conf.get("pod_vswitch_ids"), list):
                    net_ids = conf.get("pod_vswitch_ids")[0]
                    if isinstance(conf.get("worker_vswitch_ids"), list) \
                            and isinstance(conf.get("master_vswitch_ids"), list):
                        if any(net_id in net_ids for net_id in conf.get("worker_vswitch_ids")[0]):
                            self.evaluated_keys = ["worker_vswitch_ids"]
                            return CheckResult.FAILED
                        if any(net_id in net_ids for net_id in conf.get("master_vswitch_ids")[0]):
                            self.evaluated_keys = ["master_vswitch_ids"]
                            return CheckResult.FAILED
                        return CheckResult.PASSED

                self.evaluated_keys = ["pod_vswitch_ids"]
                return CheckResult.FAILED
            if "flannel" in names:
                if conf.get("pod_cidr"):
                    return CheckResult.PASSED
            self.evaluated_keys = ["addons/[0]/config"]
            return CheckResult.FAILED
        else:
            self.evaluated_keys = ["addons"]
            return CheckResult.FAILED


check = K8sEnableNetworkPolicies()
