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

resource "google_compute_shared_vpc_service_project" "projects" {
  count           = var.service_project_num
  host_project    = var.host_project_id
  service_project = element(var.service_project_ids, count.index)
}

resource "google_compute_subnetwork_iam_binding" "network_users" {
  count      = length(var.host_subnets)
  project    = var.host_project_id
  region     = element(var.host_subnet_regions, count.index)
  subnetwork = element(var.host_subnets, count.index)
  role       = "roles/compute.networkUser"

  members = compact(split(",", lookup(var.host_subnet_users,
    element(var.host_subnets, count.index))
  ))
}

resource "google_project_iam_binding" "service_agents" {
  count   = var.host_service_agent_role ? 1 : 0
  project = var.host_project_id
  role    = "roles/container.hostServiceAgentUser"
  members = var.host_service_agent_users
}
