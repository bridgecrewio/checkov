resource "kubernetes_pod_security_policy" "pass" {
  metadata {
    name = "terraform-example"
    annotations = {
      seccomp.security.alpha.kubernetes.io/defaultProfileName ="docker/default"
      "seccomp.security.alpha.kubernetes.io/defaultProfileName"="docker/default"
    }
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true
    host_ipc                   = true
    host_pid                   = true
    host_network               = true
    allowed_capabilities       = ["NET_BIND_SERVICE"]

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]
    # required_drop_capabilities = [
    #   "NET_RAW",
    #   "KILL",
    #   "SYS_TIME",
    # ]
    run_as_user {
      rule = "RunAsAny"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    read_only_root_filesystem = false
  }
}

#no annotation
resource "kubernetes_pod_security_policy" "fail" {
  metadata {
    name = "terraform-example"
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true
    host_ipc                   = true
    host_pid                   = true
    host_network               = true
    allowed_capabilities       = ["NET_BIND_SERVICE"]

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]
    # required_drop_capabilities = [
    #   "NET_RAW",
    #   "KILL",
    #   "SYS_TIME",
    # ]
    run_as_user {
      rule = "RunAsAny"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    read_only_root_filesystem = false
  }
}

#wrong annotation
resource "kubernetes_pod_security_policy" "fail2" {
  metadata {
    name = "terraform-example"
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-internal" = "false"
    }
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true
    host_ipc                   = true
    host_pid                   = true
    host_network               = true
    allowed_capabilities       = ["NET_BIND_SERVICE"]

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]
    # required_drop_capabilities = [
    #   "NET_RAW",
    #   "KILL",
    #   "SYS_TIME",
    # ]
    run_as_user {
      rule = "RunAsAny"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    read_only_root_filesystem = false
  }
}

resource "kubernetes_pod_security_policy" "fail3" {
  metadata {
    name = "terraform-example"
    annotations = {
      seccomp.security.alpha.kubernetes.io/defaultProfileName = "false"
    }
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true
    host_ipc                   = true
    host_pid                   = true
    host_network               = true
    allowed_capabilities       = ["NET_BIND_SERVICE"]

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]
    # required_drop_capabilities = [
    #   "NET_RAW",
    #   "KILL",
    #   "SYS_TIME",
    # ]
    run_as_user {
      rule = "RunAsAny"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 1
        max = 65535
      }
    }

    read_only_root_filesystem = false
  }
}
