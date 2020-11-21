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

variable "network" {
  description = "Name of the network this set of firewall rules applies to."
}

variable "project_id" {
  description = "Project id of the project that holds the network."
}

variable "internal_ranges_enabled" {
  description = "Create rules for intra-VPC ranges."
  default     = false
}

variable "internal_ranges" {
  description = "IP CIDR ranges for intra-VPC rules."
  default     = []
}

variable "internal_target_tags" {
  description = "List of target tags for intra-VPC rules."
  default     = []
}

variable "internal_allow" {
  description = "Allow rules for internal ranges."
  default = [
    {
      protocol = "icmp"
    },
  ]
}

variable "admin_ranges_enabled" {
  description = "Enable admin ranges-based rules."
  default     = false
}

variable "admin_ranges" {
  description = "IP CIDR ranges that have complete access to all subnets."
  default     = []
}

variable "ssh_source_ranges" {
  description = "List of IP CIDR ranges for tag-based SSH rule, defaults to 0.0.0.0/0."
  default     = ["0.0.0.0/0"]
}

variable "ssh_target_tags" {
  description = "List of target tags for tag-based SSH rule, defaults to ssh."
  default     = ["ssh"]
}

variable "http_source_ranges" {
  description = "List of IP CIDR ranges for tag-based HTTP rule, defaults to 0.0.0.0/0."
  default     = ["0.0.0.0/0"]
}

variable "http_target_tags" {
  description = "List of target tags for tag-based HTTP rule, defaults to http-server."
  default     = ["http-server"]
}

variable "https_source_ranges" {
  description = "List of IP CIDR ranges for tag-based HTTPS rule, defaults to 0.0.0.0/0."
  default     = ["0.0.0.0/0"]
}

variable "https_target_tags" {
  description = "List of target tags for tag-based HTTPS rule, defaults to https-server."
  default     = ["https-server"]
}

variable "custom_rules" {
  description = "List of custom rule definitions (refer to variables file for syntax)."
  default     = {}
  type = map(object({
    description          = string
    direction            = string
    action               = string # (allow|deny)
    ranges               = list(string)
    sources              = list(string)
    targets              = list(string)
    use_service_accounts = bool
    rules = list(object({
      protocol = string
      ports    = list(string)
    }))
    extra_attributes = map(string)
  }))
}
