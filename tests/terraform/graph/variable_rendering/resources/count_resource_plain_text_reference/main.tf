# https://github.com/bridgecrewio/checkov/issues/7765
# The plain text in other_secret_ref's error_message must not connect it to widget, because that closes the loop
# widget -> local.b -> other_secret_ref -> widget, and target_image, which mentions local.b, then never gets rendered.
resource "aws_elasticache_replication_group" "widget" {
  count                      = 1
  auth_token_update_strategy = local.b ? "ROTATE" : null
}

locals {
  a = aws_elasticache_replication_group.widget[0].primary_endpoint_address
  b = var.enable_other ? (var.other_mode == "required") : (var.other_secret_ref != null)
}

resource "kubernetes_deployment_v1" "target" {
  count = 1
  spec {
    template {
      spec {
        container {
          image = var.target_image
        }
      }
    }
  }
}

variable "other_mode" {
  default = "required"
}

variable "enable_other" {
  default = true
}

variable "other_secret_ref" {
  default = null
  validation {
    condition     = var.other_secret_ref == null || !var.enable_other
    error_message = "see aws_elasticache_replication_group.widget for details"
  }
}

variable "target_image" {
  description = "Pinned by tag and digest. See local.b for the gating logic."
  default     = "example/app:1.0.0@sha256:aaaa"
}
