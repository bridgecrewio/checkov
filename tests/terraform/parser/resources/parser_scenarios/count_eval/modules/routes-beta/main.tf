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

/******************************************
	Routes
 *****************************************/
resource "google_compute_route" "route" {
  provider = google-beta
  count    = var.routes_count

  project = var.project_id
  network = var.network_name

  name                   = lookup(var.routes[count.index], "name", format("%s-%s-%d", lower(var.network_name), "route", count.index))
  description            = lookup(var.routes[count.index], "description", null)
  tags                   = compact(split(",", lookup(var.routes[count.index], "tags", "")))
  dest_range             = lookup(var.routes[count.index], "destination_range", null)
  next_hop_gateway       = lookup(var.routes[count.index], "next_hop_internet", "false") == "true" ? "default-internet-gateway" : ""
  next_hop_ip            = lookup(var.routes[count.index], "next_hop_ip", null)
  next_hop_instance      = lookup(var.routes[count.index], "next_hop_instance", null)
  next_hop_instance_zone = lookup(var.routes[count.index], "next_hop_instance_zone", null)
  next_hop_vpn_tunnel    = lookup(var.routes[count.index], "next_hop_vpn_tunnel", null)
  next_hop_ilb           = lookup(var.routes[count.index], "next_hop_ilb", null)
  priority               = lookup(var.routes[count.index], "priority", null)

  depends_on = [var.module_depends_on]
}
