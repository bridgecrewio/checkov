resource "kubernetes_pod_security_policy" "fail" {
  metadata {
    name = "terraform-example"
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]

    run_as_user {
      rule = "RunAsAny"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "RunAsAny"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 0
        max = 65535
      }
    }
  }
}

resource "kubernetes_pod_security_policy" "fail2" {
  metadata {
    name = "terraform-example"
  }
}

resource "kubernetes_pod_security_policy" "pass" {
  metadata {
    name = "terraform-example"
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]

    run_as_user {
      rule = "MustRunAsNonRoot"
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "RunAsAny"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 0
        max = 65535
      }
    }
  }
}

resource "kubernetes_pod_security_policy" "fail3" {
  metadata {
    name = "terraform-example"
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]

    run_as_user {
      rule = "MustRunAs"
      range {
        max = 0
        min = 0
      }
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "RunAsAny"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 0
        max = 65535
      }
    }
  }
}

resource "kubernetes_pod_security_policy" "pass2" {
  metadata {
    name = "terraform-example"
  }
  spec {
    privileged                 = true
    allow_privilege_escalation = true

    volumes = [
      "configMap",
      "emptyDir",
      "projected",
      "secret",
      "downwardAPI",
      "persistentVolumeClaim",
    ]

    run_as_user {
      rule = "MustRunAs"
      range {
        max = 1
        min = 65535
      }
    }

    se_linux {
      rule = "RunAsAny"
    }

    supplemental_groups {
      rule = "RunAsAny"
      range {
        min = 1
        max = 65535
      }
    }

    fs_group {
      rule = "MustRunAs"
      range {
        min = 0
        max = 65535
      }
    }
  }
}