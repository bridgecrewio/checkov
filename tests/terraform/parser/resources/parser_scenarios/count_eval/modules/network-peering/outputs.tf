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

output "local_network_peering" {
  description = "Network peering resource."
  value       = google_compute_network_peering.local_network_peering
}

output "peer_network_peering" {
  description = "Peer network peering resource."
  value       = google_compute_network_peering.peer_network_peering
}

output "complete" {
  description = "Output to be used as a module dependency."
  value       = null_resource.complete.id
}
