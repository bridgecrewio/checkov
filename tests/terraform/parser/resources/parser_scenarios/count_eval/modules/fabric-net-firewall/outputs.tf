/**
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

output "internal_ranges" {
  description = "Internal ranges."

  value = {
    enabled = var.internal_ranges_enabled
    ranges  = var.internal_ranges_enabled ? join(",", var.internal_ranges) : ""
  }
}

output "admin_ranges" {
  description = "Admin ranges data."

  value = {
    enabled = var.admin_ranges_enabled
    ranges  = var.admin_ranges_enabled ? join(",", var.admin_ranges) : ""
  }
}

output "custom_ingress_allow_rules" {
  description = "Custom ingress rules with allow blocks."
  value = [
    for rule in google_compute_firewall.custom :
    rule.name if rule.direction == "INGRESS" && length(rule.allow) > 0
  ]
}

output "custom_ingress_deny_rules" {
  description = "Custom ingress rules with deny blocks."
  value = [
    for rule in google_compute_firewall.custom :
    rule.name if rule.direction == "INGRESS" && length(rule.deny) > 0
  ]
}

output "custom_egress_allow_rules" {
  description = "Custom egress rules with allow blocks."
  value = [
    for rule in google_compute_firewall.custom :
    rule.name if rule.direction == "EGRESS" && length(rule.allow) > 0
  ]
}

output "custom_egress_deny_rules" {
  description = "Custom egress rules with allow blocks."
  value = [
    for rule in google_compute_firewall.custom :
    rule.name if rule.direction == "EGRESS" && length(rule.deny) > 0
  ]
}
