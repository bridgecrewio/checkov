---
layout: default
title: kubernetes resource scans
nav_order: 1
---

# kubernetes resource scans (auto generated)

|     | Id          | Type     | Entity                 | Policy                                                                                                 | IaC        |
|-----|-------------|----------|------------------------|--------------------------------------------------------------------------------------------------------|------------|
|   0 | CKV_K8S_1   | resource | PodSecurityPolicy      | Do not admit containers wishing to share the host process ID namespace                                 | Kubernetes |
|   1 | CKV_K8S_2   | resource | PodSecurityPolicy      | Do not admit privileged containers                                                                     | Kubernetes |
|   2 | CKV_K8S_3   | resource | PodSecurityPolicy      | Do not admit containers wishing to share the host IPC namespace                                        | Kubernetes |
|   3 | CKV_K8S_4   | resource | PodSecurityPolicy      | Do not admit containers wishing to share the host network namespace                                    | Kubernetes |
|   4 | CKV_K8S_5   | resource | PodSecurityPolicy      | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|   5 | CKV_K8S_6   | resource | PodSecurityPolicy      | Do not admit root containers                                                                           | Kubernetes |
|   6 | CKV_K8S_7   | resource | PodSecurityPolicy      | Do not admit containers with the NET_RAW capability                                                    | Kubernetes |
|   7 | CKV_K8S_8   | resource | DaemonSet              | Liveness Probe Should be Configured                                                                    | Kubernetes |
|   8 | CKV_K8S_8   | resource | Deployment             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|   9 | CKV_K8S_8   | resource | Pod                    | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  10 | CKV_K8S_8   | resource | PodTemplate            | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  11 | CKV_K8S_8   | resource | ReplicaSet             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  12 | CKV_K8S_8   | resource | ReplicationController  | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  13 | CKV_K8S_8   | resource | StatefulSet            | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  14 | CKV_K8S_9   | resource | DaemonSet              | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  15 | CKV_K8S_9   | resource | Deployment             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  16 | CKV_K8S_9   | resource | Pod                    | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  17 | CKV_K8S_9   | resource | PodTemplate            | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  18 | CKV_K8S_9   | resource | ReplicaSet             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  19 | CKV_K8S_9   | resource | ReplicationController  | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  20 | CKV_K8S_9   | resource | StatefulSet            | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  21 | CKV_K8S_10  | resource | CronJob                | CPU requests should be set                                                                             | Kubernetes |
|  22 | CKV_K8S_10  | resource | DaemonSet              | CPU requests should be set                                                                             | Kubernetes |
|  23 | CKV_K8S_10  | resource | Deployment             | CPU requests should be set                                                                             | Kubernetes |
|  24 | CKV_K8S_10  | resource | Job                    | CPU requests should be set                                                                             | Kubernetes |
|  25 | CKV_K8S_10  | resource | Pod                    | CPU requests should be set                                                                             | Kubernetes |
|  26 | CKV_K8S_10  | resource | PodTemplate            | CPU requests should be set                                                                             | Kubernetes |
|  27 | CKV_K8S_10  | resource | ReplicaSet             | CPU requests should be set                                                                             | Kubernetes |
|  28 | CKV_K8S_10  | resource | ReplicationController  | CPU requests should be set                                                                             | Kubernetes |
|  29 | CKV_K8S_10  | resource | StatefulSet            | CPU requests should be set                                                                             | Kubernetes |
|  30 | CKV_K8S_11  | resource | CronJob                | CPU limits should be set                                                                               | Kubernetes |
|  31 | CKV_K8S_11  | resource | DaemonSet              | CPU limits should be set                                                                               | Kubernetes |
|  32 | CKV_K8S_11  | resource | Deployment             | CPU limits should be set                                                                               | Kubernetes |
|  33 | CKV_K8S_11  | resource | Job                    | CPU limits should be set                                                                               | Kubernetes |
|  34 | CKV_K8S_11  | resource | Pod                    | CPU limits should be set                                                                               | Kubernetes |
|  35 | CKV_K8S_11  | resource | PodTemplate            | CPU limits should be set                                                                               | Kubernetes |
|  36 | CKV_K8S_11  | resource | ReplicaSet             | CPU limits should be set                                                                               | Kubernetes |
|  37 | CKV_K8S_11  | resource | ReplicationController  | CPU limits should be set                                                                               | Kubernetes |
|  38 | CKV_K8S_11  | resource | StatefulSet            | CPU limits should be set                                                                               | Kubernetes |
|  39 | CKV_K8S_12  | resource | CronJob                | Memory requests should be set                                                                          | Kubernetes |
|  40 | CKV_K8S_12  | resource | DaemonSet              | Memory requests should be set                                                                          | Kubernetes |
|  41 | CKV_K8S_12  | resource | Deployment             | Memory requests should be set                                                                          | Kubernetes |
|  42 | CKV_K8S_12  | resource | Job                    | Memory requests should be set                                                                          | Kubernetes |
|  43 | CKV_K8S_12  | resource | Pod                    | Memory requests should be set                                                                          | Kubernetes |
|  44 | CKV_K8S_12  | resource | PodTemplate            | Memory requests should be set                                                                          | Kubernetes |
|  45 | CKV_K8S_12  | resource | ReplicaSet             | Memory requests should be set                                                                          | Kubernetes |
|  46 | CKV_K8S_12  | resource | ReplicationController  | Memory requests should be set                                                                          | Kubernetes |
|  47 | CKV_K8S_12  | resource | StatefulSet            | Memory requests should be set                                                                          | Kubernetes |
|  48 | CKV_K8S_13  | resource | CronJob                | Memory limits should be set                                                                            | Kubernetes |
|  49 | CKV_K8S_13  | resource | DaemonSet              | Memory limits should be set                                                                            | Kubernetes |
|  50 | CKV_K8S_13  | resource | Deployment             | Memory limits should be set                                                                            | Kubernetes |
|  51 | CKV_K8S_13  | resource | Job                    | Memory limits should be set                                                                            | Kubernetes |
|  52 | CKV_K8S_13  | resource | Pod                    | Memory limits should be set                                                                            | Kubernetes |
|  53 | CKV_K8S_13  | resource | PodTemplate            | Memory limits should be set                                                                            | Kubernetes |
|  54 | CKV_K8S_13  | resource | ReplicaSet             | Memory limits should be set                                                                            | Kubernetes |
|  55 | CKV_K8S_13  | resource | ReplicationController  | Memory limits should be set                                                                            | Kubernetes |
|  56 | CKV_K8S_13  | resource | StatefulSet            | Memory limits should be set                                                                            | Kubernetes |
|  57 | CKV_K8S_14  | resource | CronJob                | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  58 | CKV_K8S_14  | resource | DaemonSet              | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  59 | CKV_K8S_14  | resource | Deployment             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  60 | CKV_K8S_14  | resource | Job                    | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  61 | CKV_K8S_14  | resource | Pod                    | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  62 | CKV_K8S_14  | resource | PodTemplate            | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  63 | CKV_K8S_14  | resource | ReplicaSet             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  64 | CKV_K8S_14  | resource | ReplicationController  | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  65 | CKV_K8S_14  | resource | StatefulSet            | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  66 | CKV_K8S_15  | resource | CronJob                | Image Pull Policy should be Always                                                                     | Kubernetes |
|  67 | CKV_K8S_15  | resource | DaemonSet              | Image Pull Policy should be Always                                                                     | Kubernetes |
|  68 | CKV_K8S_15  | resource | Deployment             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  69 | CKV_K8S_15  | resource | Job                    | Image Pull Policy should be Always                                                                     | Kubernetes |
|  70 | CKV_K8S_15  | resource | Pod                    | Image Pull Policy should be Always                                                                     | Kubernetes |
|  71 | CKV_K8S_15  | resource | PodTemplate            | Image Pull Policy should be Always                                                                     | Kubernetes |
|  72 | CKV_K8S_15  | resource | ReplicaSet             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  73 | CKV_K8S_15  | resource | ReplicationController  | Image Pull Policy should be Always                                                                     | Kubernetes |
|  74 | CKV_K8S_15  | resource | StatefulSet            | Image Pull Policy should be Always                                                                     | Kubernetes |
|  75 | CKV_K8S_16  | resource | CronJob                | Container should not be privileged                                                                     | Kubernetes |
|  76 | CKV_K8S_16  | resource | DaemonSet              | Container should not be privileged                                                                     | Kubernetes |
|  77 | CKV_K8S_16  | resource | Deployment             | Container should not be privileged                                                                     | Kubernetes |
|  78 | CKV_K8S_16  | resource | Job                    | Container should not be privileged                                                                     | Kubernetes |
|  79 | CKV_K8S_16  | resource | Pod                    | Container should not be privileged                                                                     | Kubernetes |
|  80 | CKV_K8S_16  | resource | PodTemplate            | Container should not be privileged                                                                     | Kubernetes |
|  81 | CKV_K8S_16  | resource | ReplicaSet             | Container should not be privileged                                                                     | Kubernetes |
|  82 | CKV_K8S_16  | resource | ReplicationController  | Container should not be privileged                                                                     | Kubernetes |
|  83 | CKV_K8S_16  | resource | StatefulSet            | Container should not be privileged                                                                     | Kubernetes |
|  84 | CKV_K8S_17  | resource | CronJob                | Containers should not share the host process ID namespace                                              | Kubernetes |
|  85 | CKV_K8S_17  | resource | DaemonSet              | Containers should not share the host process ID namespace                                              | Kubernetes |
|  86 | CKV_K8S_17  | resource | Deployment             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  87 | CKV_K8S_17  | resource | Job                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  88 | CKV_K8S_17  | resource | Pod                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  89 | CKV_K8S_17  | resource | ReplicaSet             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  90 | CKV_K8S_17  | resource | ReplicationController  | Containers should not share the host process ID namespace                                              | Kubernetes |
|  91 | CKV_K8S_17  | resource | StatefulSet            | Containers should not share the host process ID namespace                                              | Kubernetes |
|  92 | CKV_K8S_18  | resource | CronJob                | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  93 | CKV_K8S_18  | resource | DaemonSet              | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  94 | CKV_K8S_18  | resource | Deployment             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  95 | CKV_K8S_18  | resource | Job                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  96 | CKV_K8S_18  | resource | Pod                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  97 | CKV_K8S_18  | resource | ReplicaSet             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  98 | CKV_K8S_18  | resource | ReplicationController  | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  99 | CKV_K8S_18  | resource | StatefulSet            | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 100 | CKV_K8S_19  | resource | CronJob                | Containers should not share the host network namespace                                                 | Kubernetes |
| 101 | CKV_K8S_19  | resource | DaemonSet              | Containers should not share the host network namespace                                                 | Kubernetes |
| 102 | CKV_K8S_19  | resource | Deployment             | Containers should not share the host network namespace                                                 | Kubernetes |
| 103 | CKV_K8S_19  | resource | Job                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 104 | CKV_K8S_19  | resource | Pod                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 105 | CKV_K8S_19  | resource | ReplicaSet             | Containers should not share the host network namespace                                                 | Kubernetes |
| 106 | CKV_K8S_19  | resource | ReplicationController  | Containers should not share the host network namespace                                                 | Kubernetes |
| 107 | CKV_K8S_19  | resource | StatefulSet            | Containers should not share the host network namespace                                                 | Kubernetes |
| 108 | CKV_K8S_20  | resource | CronJob                | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 109 | CKV_K8S_20  | resource | DaemonSet              | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 110 | CKV_K8S_20  | resource | Deployment             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 111 | CKV_K8S_20  | resource | Job                    | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 112 | CKV_K8S_20  | resource | Pod                    | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 113 | CKV_K8S_20  | resource | PodTemplate            | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 114 | CKV_K8S_20  | resource | ReplicaSet             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 115 | CKV_K8S_20  | resource | ReplicationController  | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 116 | CKV_K8S_20  | resource | StatefulSet            | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 117 | CKV_K8S_21  | resource | ConfigMap              | The default namespace should not be used                                                               | Kubernetes |
| 118 | CKV_K8S_21  | resource | CronJob                | The default namespace should not be used                                                               | Kubernetes |
| 119 | CKV_K8S_21  | resource | DaemonSet              | The default namespace should not be used                                                               | Kubernetes |
| 120 | CKV_K8S_21  | resource | Deployment             | The default namespace should not be used                                                               | Kubernetes |
| 121 | CKV_K8S_21  | resource | Ingress                | The default namespace should not be used                                                               | Kubernetes |
| 122 | CKV_K8S_21  | resource | Job                    | The default namespace should not be used                                                               | Kubernetes |
| 123 | CKV_K8S_21  | resource | Pod                    | The default namespace should not be used                                                               | Kubernetes |
| 124 | CKV_K8S_21  | resource | ReplicaSet             | The default namespace should not be used                                                               | Kubernetes |
| 125 | CKV_K8S_21  | resource | ReplicationController  | The default namespace should not be used                                                               | Kubernetes |
| 126 | CKV_K8S_21  | resource | Role                   | The default namespace should not be used                                                               | Kubernetes |
| 127 | CKV_K8S_21  | resource | RoleBinding            | The default namespace should not be used                                                               | Kubernetes |
| 128 | CKV_K8S_21  | resource | Secret                 | The default namespace should not be used                                                               | Kubernetes |
| 129 | CKV_K8S_21  | resource | Service                | The default namespace should not be used                                                               | Kubernetes |
| 130 | CKV_K8S_21  | resource | ServiceAccount         | The default namespace should not be used                                                               | Kubernetes |
| 131 | CKV_K8S_21  | resource | StatefulSet            | The default namespace should not be used                                                               | Kubernetes |
| 132 | CKV_K8S_22  | resource | CronJob                | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 133 | CKV_K8S_22  | resource | DaemonSet              | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 134 | CKV_K8S_22  | resource | Deployment             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 135 | CKV_K8S_22  | resource | Job                    | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 136 | CKV_K8S_22  | resource | Pod                    | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 137 | CKV_K8S_22  | resource | PodTemplate            | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 138 | CKV_K8S_22  | resource | ReplicaSet             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 139 | CKV_K8S_22  | resource | ReplicationController  | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 140 | CKV_K8S_22  | resource | StatefulSet            | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 141 | CKV_K8S_23  | resource | CronJob                | Minimize the admission of root containers                                                              | Kubernetes |
| 142 | CKV_K8S_23  | resource | DaemonSet              | Minimize the admission of root containers                                                              | Kubernetes |
| 143 | CKV_K8S_23  | resource | Deployment             | Minimize the admission of root containers                                                              | Kubernetes |
| 144 | CKV_K8S_23  | resource | Job                    | Minimize the admission of root containers                                                              | Kubernetes |
| 145 | CKV_K8S_23  | resource | Pod                    | Minimize the admission of root containers                                                              | Kubernetes |
| 146 | CKV_K8S_23  | resource | ReplicaSet             | Minimize the admission of root containers                                                              | Kubernetes |
| 147 | CKV_K8S_23  | resource | ReplicationController  | Minimize the admission of root containers                                                              | Kubernetes |
| 148 | CKV_K8S_23  | resource | StatefulSet            | Minimize the admission of root containers                                                              | Kubernetes |
| 149 | CKV_K8S_24  | resource | PodSecurityPolicy      | Do not allow containers with added capability                                                          | Kubernetes |
| 150 | CKV_K8S_25  | resource | CronJob                | Minimize the admission of containers with added capability                                             | Kubernetes |
| 151 | CKV_K8S_25  | resource | DaemonSet              | Minimize the admission of containers with added capability                                             | Kubernetes |
| 152 | CKV_K8S_25  | resource | Deployment             | Minimize the admission of containers with added capability                                             | Kubernetes |
| 153 | CKV_K8S_25  | resource | Job                    | Minimize the admission of containers with added capability                                             | Kubernetes |
| 154 | CKV_K8S_25  | resource | Pod                    | Minimize the admission of containers with added capability                                             | Kubernetes |
| 155 | CKV_K8S_25  | resource | PodTemplate            | Minimize the admission of containers with added capability                                             | Kubernetes |
| 156 | CKV_K8S_25  | resource | ReplicaSet             | Minimize the admission of containers with added capability                                             | Kubernetes |
| 157 | CKV_K8S_25  | resource | ReplicationController  | Minimize the admission of containers with added capability                                             | Kubernetes |
| 158 | CKV_K8S_25  | resource | StatefulSet            | Minimize the admission of containers with added capability                                             | Kubernetes |
| 159 | CKV_K8S_26  | resource | CronJob                | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 160 | CKV_K8S_26  | resource | DaemonSet              | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 161 | CKV_K8S_26  | resource | Deployment             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 162 | CKV_K8S_26  | resource | Job                    | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 163 | CKV_K8S_26  | resource | Pod                    | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 164 | CKV_K8S_26  | resource | PodTemplate            | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 165 | CKV_K8S_26  | resource | ReplicaSet             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 166 | CKV_K8S_26  | resource | ReplicationController  | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 167 | CKV_K8S_26  | resource | StatefulSet            | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 168 | CKV_K8S_27  | resource | CronJob                | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 169 | CKV_K8S_27  | resource | DaemonSet              | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 170 | CKV_K8S_27  | resource | Deployment             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 171 | CKV_K8S_27  | resource | Job                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 172 | CKV_K8S_27  | resource | Pod                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 173 | CKV_K8S_27  | resource | ReplicaSet             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 174 | CKV_K8S_27  | resource | ReplicationController  | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 175 | CKV_K8S_27  | resource | StatefulSet            | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 176 | CKV_K8S_28  | resource | CronJob                | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 177 | CKV_K8S_28  | resource | DaemonSet              | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 178 | CKV_K8S_28  | resource | Deployment             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 179 | CKV_K8S_28  | resource | Job                    | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 180 | CKV_K8S_28  | resource | Pod                    | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 181 | CKV_K8S_28  | resource | PodTemplate            | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 182 | CKV_K8S_28  | resource | ReplicaSet             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 183 | CKV_K8S_28  | resource | ReplicationController  | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 184 | CKV_K8S_28  | resource | StatefulSet            | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 185 | CKV_K8S_29  | resource | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
| 186 | CKV_K8S_29  | resource | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
| 187 | CKV_K8S_29  | resource | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
| 188 | CKV_K8S_29  | resource | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 189 | CKV_K8S_29  | resource | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 190 | CKV_K8S_29  | resource | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
| 191 | CKV_K8S_29  | resource | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
| 192 | CKV_K8S_29  | resource | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
| 193 | CKV_K8S_30  | resource | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
| 194 | CKV_K8S_30  | resource | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
| 195 | CKV_K8S_30  | resource | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
| 196 | CKV_K8S_30  | resource | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 197 | CKV_K8S_30  | resource | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 198 | CKV_K8S_30  | resource | PodTemplate            | Apply security context to your pods and containers                                                     | Kubernetes |
| 199 | CKV_K8S_30  | resource | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
| 200 | CKV_K8S_30  | resource | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
| 201 | CKV_K8S_30  | resource | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
| 202 | CKV_K8S_31  | resource | CronJob                | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 203 | CKV_K8S_31  | resource | DaemonSet              | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 204 | CKV_K8S_31  | resource | Deployment             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 205 | CKV_K8S_31  | resource | Job                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 206 | CKV_K8S_31  | resource | Pod                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 207 | CKV_K8S_31  | resource | ReplicaSet             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 208 | CKV_K8S_31  | resource | ReplicationController  | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 209 | CKV_K8S_31  | resource | StatefulSet            | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 210 | CKV_K8S_32  | resource | PodSecurityPolicy      | Ensure default seccomp profile set to docker/default or runtime/default                                | Kubernetes |
| 211 | CKV_K8S_33  | resource | CronJob                | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 212 | CKV_K8S_33  | resource | DaemonSet              | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 213 | CKV_K8S_33  | resource | Deployment             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 214 | CKV_K8S_33  | resource | Job                    | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 215 | CKV_K8S_33  | resource | Pod                    | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 216 | CKV_K8S_33  | resource | PodTemplate            | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 217 | CKV_K8S_33  | resource | ReplicaSet             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 218 | CKV_K8S_33  | resource | ReplicationController  | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 219 | CKV_K8S_33  | resource | StatefulSet            | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 220 | CKV_K8S_34  | resource | CronJob                | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 221 | CKV_K8S_34  | resource | DaemonSet              | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 222 | CKV_K8S_34  | resource | Deployment             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 223 | CKV_K8S_34  | resource | Job                    | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 224 | CKV_K8S_34  | resource | Pod                    | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 225 | CKV_K8S_34  | resource | PodTemplate            | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 226 | CKV_K8S_34  | resource | ReplicaSet             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 227 | CKV_K8S_34  | resource | ReplicationController  | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 228 | CKV_K8S_34  | resource | StatefulSet            | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 229 | CKV_K8S_35  | resource | CronJob                | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 230 | CKV_K8S_35  | resource | DaemonSet              | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 231 | CKV_K8S_35  | resource | Deployment             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 232 | CKV_K8S_35  | resource | Job                    | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 233 | CKV_K8S_35  | resource | Pod                    | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 234 | CKV_K8S_35  | resource | PodTemplate            | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 235 | CKV_K8S_35  | resource | ReplicaSet             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 236 | CKV_K8S_35  | resource | ReplicationController  | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 237 | CKV_K8S_35  | resource | StatefulSet            | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 238 | CKV_K8S_36  | resource | PodSecurityPolicy      | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 239 | CKV_K8S_37  | resource | CronJob                | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 240 | CKV_K8S_37  | resource | DaemonSet              | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 241 | CKV_K8S_37  | resource | Deployment             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 242 | CKV_K8S_37  | resource | Job                    | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 243 | CKV_K8S_37  | resource | Pod                    | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 244 | CKV_K8S_37  | resource | PodTemplate            | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 245 | CKV_K8S_37  | resource | ReplicaSet             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 246 | CKV_K8S_37  | resource | ReplicationController  | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 247 | CKV_K8S_37  | resource | StatefulSet            | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 248 | CKV_K8S_38  | resource | CronJob                | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 249 | CKV_K8S_38  | resource | DaemonSet              | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 250 | CKV_K8S_38  | resource | Deployment             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 251 | CKV_K8S_38  | resource | Job                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 252 | CKV_K8S_38  | resource | Pod                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 253 | CKV_K8S_38  | resource | ReplicaSet             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 254 | CKV_K8S_38  | resource | ReplicationController  | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 255 | CKV_K8S_38  | resource | StatefulSet            | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 256 | CKV_K8S_39  | resource | CronJob                | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 257 | CKV_K8S_39  | resource | DaemonSet              | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 258 | CKV_K8S_39  | resource | Deployment             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 259 | CKV_K8S_39  | resource | Job                    | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 260 | CKV_K8S_39  | resource | Pod                    | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 261 | CKV_K8S_39  | resource | PodTemplate            | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 262 | CKV_K8S_39  | resource | ReplicaSet             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 263 | CKV_K8S_39  | resource | ReplicationController  | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 264 | CKV_K8S_39  | resource | StatefulSet            | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 265 | CKV_K8S_40  | resource | CronJob                | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 266 | CKV_K8S_40  | resource | DaemonSet              | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 267 | CKV_K8S_40  | resource | Deployment             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 268 | CKV_K8S_40  | resource | Job                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 269 | CKV_K8S_40  | resource | Pod                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 270 | CKV_K8S_40  | resource | ReplicaSet             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 271 | CKV_K8S_40  | resource | ReplicationController  | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 272 | CKV_K8S_40  | resource | StatefulSet            | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 273 | CKV_K8S_41  | resource | ServiceAccount         | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 274 | CKV_K8S_42  | resource | ClusterRoleBinding     | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 275 | CKV_K8S_42  | resource | RoleBinding            | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 276 | CKV_K8S_43  | resource | CronJob                | Image should use digest                                                                                | Kubernetes |
| 277 | CKV_K8S_43  | resource | DaemonSet              | Image should use digest                                                                                | Kubernetes |
| 278 | CKV_K8S_43  | resource | Deployment             | Image should use digest                                                                                | Kubernetes |
| 279 | CKV_K8S_43  | resource | Job                    | Image should use digest                                                                                | Kubernetes |
| 280 | CKV_K8S_43  | resource | Pod                    | Image should use digest                                                                                | Kubernetes |
| 281 | CKV_K8S_43  | resource | PodTemplate            | Image should use digest                                                                                | Kubernetes |
| 282 | CKV_K8S_43  | resource | ReplicaSet             | Image should use digest                                                                                | Kubernetes |
| 283 | CKV_K8S_43  | resource | ReplicationController  | Image should use digest                                                                                | Kubernetes |
| 284 | CKV_K8S_43  | resource | StatefulSet            | Image should use digest                                                                                | Kubernetes |
| 285 | CKV_K8S_44  | resource | Service                | Ensure that the Tiller Service (Helm v2) is deleted                                                    | Kubernetes |
| 286 | CKV_K8S_45  | resource | CronJob                | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 287 | CKV_K8S_45  | resource | DaemonSet              | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 288 | CKV_K8S_45  | resource | Deployment             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 289 | CKV_K8S_45  | resource | Job                    | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 290 | CKV_K8S_45  | resource | Pod                    | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 291 | CKV_K8S_45  | resource | PodTemplate            | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 292 | CKV_K8S_45  | resource | ReplicaSet             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 293 | CKV_K8S_45  | resource | ReplicationController  | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 294 | CKV_K8S_45  | resource | StatefulSet            | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 295 | CKV_K8S_49  | resource | ClusterRole            | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 296 | CKV_K8S_49  | resource | Role                   | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 297 | CKV_K8S_68  | resource | CronJob                | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 298 | CKV_K8S_68  | resource | DaemonSet              | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 299 | CKV_K8S_68  | resource | Deployment             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 300 | CKV_K8S_68  | resource | Job                    | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 301 | CKV_K8S_68  | resource | Pod                    | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 302 | CKV_K8S_68  | resource | PodTemplate            | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 303 | CKV_K8S_68  | resource | ReplicaSet             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 304 | CKV_K8S_68  | resource | ReplicationController  | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 305 | CKV_K8S_68  | resource | StatefulSet            | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 306 | CKV_K8S_69  | resource | CronJob                | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 307 | CKV_K8S_69  | resource | DaemonSet              | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 308 | CKV_K8S_69  | resource | Deployment             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 309 | CKV_K8S_69  | resource | Job                    | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 310 | CKV_K8S_69  | resource | Pod                    | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 311 | CKV_K8S_69  | resource | PodTemplate            | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 312 | CKV_K8S_69  | resource | ReplicaSet             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 313 | CKV_K8S_69  | resource | ReplicationController  | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 314 | CKV_K8S_69  | resource | StatefulSet            | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 315 | CKV_K8S_70  | resource | CronJob                | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 316 | CKV_K8S_70  | resource | DaemonSet              | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 317 | CKV_K8S_70  | resource | Deployment             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 318 | CKV_K8S_70  | resource | Job                    | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 319 | CKV_K8S_70  | resource | Pod                    | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 320 | CKV_K8S_70  | resource | PodTemplate            | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 321 | CKV_K8S_70  | resource | ReplicaSet             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 322 | CKV_K8S_70  | resource | ReplicationController  | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 323 | CKV_K8S_70  | resource | StatefulSet            | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 324 | CKV_K8S_71  | resource | CronJob                | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 325 | CKV_K8S_71  | resource | DaemonSet              | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 326 | CKV_K8S_71  | resource | Deployment             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 327 | CKV_K8S_71  | resource | Job                    | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 328 | CKV_K8S_71  | resource | Pod                    | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 329 | CKV_K8S_71  | resource | PodTemplate            | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 330 | CKV_K8S_71  | resource | ReplicaSet             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 331 | CKV_K8S_71  | resource | ReplicationController  | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 332 | CKV_K8S_71  | resource | StatefulSet            | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 333 | CKV_K8S_72  | resource | CronJob                | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 334 | CKV_K8S_72  | resource | DaemonSet              | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 335 | CKV_K8S_72  | resource | Deployment             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 336 | CKV_K8S_72  | resource | Job                    | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 337 | CKV_K8S_72  | resource | Pod                    | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 338 | CKV_K8S_72  | resource | PodTemplate            | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 339 | CKV_K8S_72  | resource | ReplicaSet             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 340 | CKV_K8S_72  | resource | ReplicationController  | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 341 | CKV_K8S_72  | resource | StatefulSet            | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 342 | CKV_K8S_73  | resource | CronJob                | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 343 | CKV_K8S_73  | resource | DaemonSet              | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 344 | CKV_K8S_73  | resource | Deployment             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 345 | CKV_K8S_73  | resource | Job                    | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 346 | CKV_K8S_73  | resource | Pod                    | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 347 | CKV_K8S_73  | resource | PodTemplate            | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 348 | CKV_K8S_73  | resource | ReplicaSet             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 349 | CKV_K8S_73  | resource | ReplicationController  | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 350 | CKV_K8S_73  | resource | StatefulSet            | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 351 | CKV_K8S_74  | resource | CronJob                | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 352 | CKV_K8S_74  | resource | DaemonSet              | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 353 | CKV_K8S_74  | resource | Deployment             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 354 | CKV_K8S_74  | resource | Job                    | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 355 | CKV_K8S_74  | resource | Pod                    | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 356 | CKV_K8S_74  | resource | PodTemplate            | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 357 | CKV_K8S_74  | resource | ReplicaSet             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 358 | CKV_K8S_74  | resource | ReplicationController  | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 359 | CKV_K8S_74  | resource | StatefulSet            | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 360 | CKV_K8S_75  | resource | CronJob                | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 361 | CKV_K8S_75  | resource | DaemonSet              | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 362 | CKV_K8S_75  | resource | Deployment             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 363 | CKV_K8S_75  | resource | Job                    | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 364 | CKV_K8S_75  | resource | Pod                    | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 365 | CKV_K8S_75  | resource | PodTemplate            | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 366 | CKV_K8S_75  | resource | ReplicaSet             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 367 | CKV_K8S_75  | resource | ReplicationController  | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 368 | CKV_K8S_75  | resource | StatefulSet            | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 369 | CKV_K8S_77  | resource | CronJob                | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 370 | CKV_K8S_77  | resource | DaemonSet              | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 371 | CKV_K8S_77  | resource | Deployment             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 372 | CKV_K8S_77  | resource | Job                    | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 373 | CKV_K8S_77  | resource | Pod                    | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 374 | CKV_K8S_77  | resource | PodTemplate            | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 375 | CKV_K8S_77  | resource | ReplicaSet             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 376 | CKV_K8S_77  | resource | ReplicationController  | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 377 | CKV_K8S_77  | resource | StatefulSet            | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 378 | CKV_K8S_78  | resource | AdmissionConfiguration | Ensure that the admission control plugin EventRateLimit is set                                         | Kubernetes |
| 379 | CKV_K8S_79  | resource | CronJob                | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 380 | CKV_K8S_79  | resource | DaemonSet              | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 381 | CKV_K8S_79  | resource | Deployment             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 382 | CKV_K8S_79  | resource | Job                    | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 383 | CKV_K8S_79  | resource | Pod                    | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 384 | CKV_K8S_79  | resource | PodTemplate            | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 385 | CKV_K8S_79  | resource | ReplicaSet             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 386 | CKV_K8S_79  | resource | ReplicationController  | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 387 | CKV_K8S_79  | resource | StatefulSet            | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 388 | CKV_K8S_80  | resource | CronJob                | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 389 | CKV_K8S_80  | resource | DaemonSet              | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 390 | CKV_K8S_80  | resource | Deployment             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 391 | CKV_K8S_80  | resource | Job                    | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 392 | CKV_K8S_80  | resource | Pod                    | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 393 | CKV_K8S_80  | resource | PodTemplate            | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 394 | CKV_K8S_80  | resource | ReplicaSet             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 395 | CKV_K8S_80  | resource | ReplicationController  | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 396 | CKV_K8S_80  | resource | StatefulSet            | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 397 | CKV_K8S_81  | resource | CronJob                | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 398 | CKV_K8S_81  | resource | DaemonSet              | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 399 | CKV_K8S_81  | resource | Deployment             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 400 | CKV_K8S_81  | resource | Job                    | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 401 | CKV_K8S_81  | resource | Pod                    | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 402 | CKV_K8S_81  | resource | PodTemplate            | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 403 | CKV_K8S_81  | resource | ReplicaSet             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 404 | CKV_K8S_81  | resource | ReplicationController  | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 405 | CKV_K8S_81  | resource | StatefulSet            | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 406 | CKV_K8S_82  | resource | CronJob                | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 407 | CKV_K8S_82  | resource | DaemonSet              | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 408 | CKV_K8S_82  | resource | Deployment             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 409 | CKV_K8S_82  | resource | Job                    | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 410 | CKV_K8S_82  | resource | Pod                    | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 411 | CKV_K8S_82  | resource | PodTemplate            | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 412 | CKV_K8S_82  | resource | ReplicaSet             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 413 | CKV_K8S_82  | resource | ReplicationController  | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 414 | CKV_K8S_82  | resource | StatefulSet            | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 415 | CKV_K8S_83  | resource | CronJob                | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 416 | CKV_K8S_83  | resource | DaemonSet              | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 417 | CKV_K8S_83  | resource | Deployment             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 418 | CKV_K8S_83  | resource | Job                    | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 419 | CKV_K8S_83  | resource | Pod                    | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 420 | CKV_K8S_83  | resource | PodTemplate            | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 421 | CKV_K8S_83  | resource | ReplicaSet             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 422 | CKV_K8S_83  | resource | ReplicationController  | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 423 | CKV_K8S_83  | resource | StatefulSet            | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 424 | CKV_K8S_84  | resource | CronJob                | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 425 | CKV_K8S_84  | resource | DaemonSet              | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 426 | CKV_K8S_84  | resource | Deployment             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 427 | CKV_K8S_84  | resource | Job                    | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 428 | CKV_K8S_84  | resource | Pod                    | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 429 | CKV_K8S_84  | resource | PodTemplate            | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 430 | CKV_K8S_84  | resource | ReplicaSet             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 431 | CKV_K8S_84  | resource | ReplicationController  | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 432 | CKV_K8S_84  | resource | StatefulSet            | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 433 | CKV_K8S_85  | resource | CronJob                | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 434 | CKV_K8S_85  | resource | DaemonSet              | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 435 | CKV_K8S_85  | resource | Deployment             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 436 | CKV_K8S_85  | resource | Job                    | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 437 | CKV_K8S_85  | resource | Pod                    | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 438 | CKV_K8S_85  | resource | PodTemplate            | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 439 | CKV_K8S_85  | resource | ReplicaSet             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 440 | CKV_K8S_85  | resource | ReplicationController  | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 441 | CKV_K8S_85  | resource | StatefulSet            | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 442 | CKV_K8S_86  | resource | CronJob                | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 443 | CKV_K8S_86  | resource | DaemonSet              | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 444 | CKV_K8S_86  | resource | Deployment             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 445 | CKV_K8S_86  | resource | Job                    | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 446 | CKV_K8S_86  | resource | Pod                    | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 447 | CKV_K8S_86  | resource | PodTemplate            | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 448 | CKV_K8S_86  | resource | ReplicaSet             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 449 | CKV_K8S_86  | resource | ReplicationController  | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 450 | CKV_K8S_86  | resource | StatefulSet            | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 451 | CKV_K8S_88  | resource | CronJob                | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 452 | CKV_K8S_88  | resource | DaemonSet              | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 453 | CKV_K8S_88  | resource | Deployment             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 454 | CKV_K8S_88  | resource | Job                    | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 455 | CKV_K8S_88  | resource | Pod                    | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 456 | CKV_K8S_88  | resource | PodTemplate            | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 457 | CKV_K8S_88  | resource | ReplicaSet             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 458 | CKV_K8S_88  | resource | ReplicationController  | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 459 | CKV_K8S_88  | resource | StatefulSet            | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 460 | CKV_K8S_89  | resource | CronJob                | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 461 | CKV_K8S_89  | resource | DaemonSet              | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 462 | CKV_K8S_89  | resource | Deployment             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 463 | CKV_K8S_89  | resource | Job                    | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 464 | CKV_K8S_89  | resource | Pod                    | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 465 | CKV_K8S_89  | resource | PodTemplate            | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 466 | CKV_K8S_89  | resource | ReplicaSet             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 467 | CKV_K8S_89  | resource | ReplicationController  | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 468 | CKV_K8S_89  | resource | StatefulSet            | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 469 | CKV_K8S_90  | resource | CronJob                | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 470 | CKV_K8S_90  | resource | DaemonSet              | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 471 | CKV_K8S_90  | resource | Deployment             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 472 | CKV_K8S_90  | resource | Job                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 473 | CKV_K8S_90  | resource | Pod                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 474 | CKV_K8S_90  | resource | PodTemplate            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 475 | CKV_K8S_90  | resource | ReplicaSet             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 476 | CKV_K8S_90  | resource | ReplicationController  | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 477 | CKV_K8S_90  | resource | StatefulSet            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 478 | CKV_K8S_91  | resource | CronJob                | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 479 | CKV_K8S_91  | resource | DaemonSet              | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 480 | CKV_K8S_91  | resource | Deployment             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 481 | CKV_K8S_91  | resource | Job                    | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 482 | CKV_K8S_91  | resource | Pod                    | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 483 | CKV_K8S_91  | resource | PodTemplate            | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 484 | CKV_K8S_91  | resource | ReplicaSet             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 485 | CKV_K8S_91  | resource | ReplicationController  | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 486 | CKV_K8S_91  | resource | StatefulSet            | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 487 | CKV_K8S_92  | resource | CronJob                | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 488 | CKV_K8S_92  | resource | DaemonSet              | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 489 | CKV_K8S_92  | resource | Deployment             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 490 | CKV_K8S_92  | resource | Job                    | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 491 | CKV_K8S_92  | resource | Pod                    | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 492 | CKV_K8S_92  | resource | PodTemplate            | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 493 | CKV_K8S_92  | resource | ReplicaSet             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 494 | CKV_K8S_92  | resource | ReplicationController  | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 495 | CKV_K8S_92  | resource | StatefulSet            | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 496 | CKV_K8S_93  | resource | CronJob                | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 497 | CKV_K8S_93  | resource | DaemonSet              | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 498 | CKV_K8S_93  | resource | Deployment             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 499 | CKV_K8S_93  | resource | Job                    | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 500 | CKV_K8S_93  | resource | Pod                    | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 501 | CKV_K8S_93  | resource | PodTemplate            | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 502 | CKV_K8S_93  | resource | ReplicaSet             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 503 | CKV_K8S_93  | resource | ReplicationController  | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 504 | CKV_K8S_93  | resource | StatefulSet            | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 505 | CKV_K8S_94  | resource | CronJob                | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 506 | CKV_K8S_94  | resource | DaemonSet              | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 507 | CKV_K8S_94  | resource | Deployment             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 508 | CKV_K8S_94  | resource | Job                    | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 509 | CKV_K8S_94  | resource | Pod                    | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 510 | CKV_K8S_94  | resource | PodTemplate            | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 511 | CKV_K8S_94  | resource | ReplicaSet             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 512 | CKV_K8S_94  | resource | ReplicationController  | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 513 | CKV_K8S_94  | resource | StatefulSet            | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 514 | CKV_K8S_95  | resource | CronJob                | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 515 | CKV_K8S_95  | resource | DaemonSet              | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 516 | CKV_K8S_95  | resource | Deployment             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 517 | CKV_K8S_95  | resource | Job                    | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 518 | CKV_K8S_95  | resource | Pod                    | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 519 | CKV_K8S_95  | resource | PodTemplate            | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 520 | CKV_K8S_95  | resource | ReplicaSet             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 521 | CKV_K8S_95  | resource | ReplicationController  | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 522 | CKV_K8S_95  | resource | StatefulSet            | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 523 | CKV_K8S_96  | resource | CronJob                | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 524 | CKV_K8S_96  | resource | DaemonSet              | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 525 | CKV_K8S_96  | resource | Deployment             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 526 | CKV_K8S_96  | resource | Job                    | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 527 | CKV_K8S_96  | resource | Pod                    | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 528 | CKV_K8S_96  | resource | PodTemplate            | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 529 | CKV_K8S_96  | resource | ReplicaSet             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 530 | CKV_K8S_96  | resource | ReplicationController  | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 531 | CKV_K8S_96  | resource | StatefulSet            | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 532 | CKV_K8S_97  | resource | CronJob                | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 533 | CKV_K8S_97  | resource | DaemonSet              | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 534 | CKV_K8S_97  | resource | Deployment             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 535 | CKV_K8S_97  | resource | Job                    | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 536 | CKV_K8S_97  | resource | Pod                    | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 537 | CKV_K8S_97  | resource | PodTemplate            | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 538 | CKV_K8S_97  | resource | ReplicaSet             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 539 | CKV_K8S_97  | resource | ReplicationController  | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 540 | CKV_K8S_97  | resource | StatefulSet            | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 541 | CKV_K8S_99  | resource | CronJob                | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 542 | CKV_K8S_99  | resource | DaemonSet              | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 543 | CKV_K8S_99  | resource | Deployment             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 544 | CKV_K8S_99  | resource | Job                    | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 545 | CKV_K8S_99  | resource | Pod                    | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 546 | CKV_K8S_99  | resource | PodTemplate            | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 547 | CKV_K8S_99  | resource | ReplicaSet             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 548 | CKV_K8S_99  | resource | ReplicationController  | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 549 | CKV_K8S_99  | resource | StatefulSet            | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 550 | CKV_K8S_100 | resource | CronJob                | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 551 | CKV_K8S_100 | resource | DaemonSet              | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 552 | CKV_K8S_100 | resource | Deployment             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 553 | CKV_K8S_100 | resource | Job                    | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 554 | CKV_K8S_100 | resource | Pod                    | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 555 | CKV_K8S_100 | resource | PodTemplate            | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 556 | CKV_K8S_100 | resource | ReplicaSet             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 557 | CKV_K8S_100 | resource | ReplicationController  | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 558 | CKV_K8S_100 | resource | StatefulSet            | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 559 | CKV_K8S_102 | resource | CronJob                | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 560 | CKV_K8S_102 | resource | DaemonSet              | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 561 | CKV_K8S_102 | resource | Deployment             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 562 | CKV_K8S_102 | resource | Job                    | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 563 | CKV_K8S_102 | resource | Pod                    | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 564 | CKV_K8S_102 | resource | PodTemplate            | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 565 | CKV_K8S_102 | resource | ReplicaSet             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 566 | CKV_K8S_102 | resource | ReplicationController  | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 567 | CKV_K8S_102 | resource | StatefulSet            | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 568 | CKV_K8S_104 | resource | CronJob                | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 569 | CKV_K8S_104 | resource | DaemonSet              | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 570 | CKV_K8S_104 | resource | Deployment             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 571 | CKV_K8S_104 | resource | Job                    | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 572 | CKV_K8S_104 | resource | Pod                    | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 573 | CKV_K8S_104 | resource | PodTemplate            | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 574 | CKV_K8S_104 | resource | ReplicaSet             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 575 | CKV_K8S_104 | resource | ReplicationController  | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 576 | CKV_K8S_104 | resource | StatefulSet            | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 577 | CKV_K8S_105 | resource | CronJob                | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 578 | CKV_K8S_105 | resource | DaemonSet              | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 579 | CKV_K8S_105 | resource | Deployment             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 580 | CKV_K8S_105 | resource | Job                    | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 581 | CKV_K8S_105 | resource | Pod                    | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 582 | CKV_K8S_105 | resource | PodTemplate            | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 583 | CKV_K8S_105 | resource | ReplicaSet             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 584 | CKV_K8S_105 | resource | ReplicationController  | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 585 | CKV_K8S_105 | resource | StatefulSet            | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 586 | CKV_K8S_106 | resource | CronJob                | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 587 | CKV_K8S_106 | resource | DaemonSet              | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 588 | CKV_K8S_106 | resource | Deployment             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 589 | CKV_K8S_106 | resource | Job                    | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 590 | CKV_K8S_106 | resource | Pod                    | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 591 | CKV_K8S_106 | resource | PodTemplate            | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 592 | CKV_K8S_106 | resource | ReplicaSet             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 593 | CKV_K8S_106 | resource | ReplicationController  | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 594 | CKV_K8S_106 | resource | StatefulSet            | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 595 | CKV_K8S_107 | resource | CronJob                | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 596 | CKV_K8S_107 | resource | DaemonSet              | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 597 | CKV_K8S_107 | resource | Deployment             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 598 | CKV_K8S_107 | resource | Job                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 599 | CKV_K8S_107 | resource | Pod                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 600 | CKV_K8S_107 | resource | PodTemplate            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 601 | CKV_K8S_107 | resource | ReplicaSet             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 602 | CKV_K8S_107 | resource | ReplicationController  | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 603 | CKV_K8S_107 | resource | StatefulSet            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 604 | CKV_K8S_108 | resource | CronJob                | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 605 | CKV_K8S_108 | resource | DaemonSet              | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 606 | CKV_K8S_108 | resource | Deployment             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 607 | CKV_K8S_108 | resource | Job                    | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 608 | CKV_K8S_108 | resource | Pod                    | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 609 | CKV_K8S_108 | resource | PodTemplate            | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 610 | CKV_K8S_108 | resource | ReplicaSet             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 611 | CKV_K8S_108 | resource | ReplicationController  | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 612 | CKV_K8S_108 | resource | StatefulSet            | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 613 | CKV_K8S_110 | resource | CronJob                | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 614 | CKV_K8S_110 | resource | DaemonSet              | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 615 | CKV_K8S_110 | resource | Deployment             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 616 | CKV_K8S_110 | resource | Job                    | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 617 | CKV_K8S_110 | resource | Pod                    | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 618 | CKV_K8S_110 | resource | PodTemplate            | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 619 | CKV_K8S_110 | resource | ReplicaSet             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 620 | CKV_K8S_110 | resource | ReplicationController  | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 621 | CKV_K8S_110 | resource | StatefulSet            | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 622 | CKV_K8S_111 | resource | CronJob                | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 623 | CKV_K8S_111 | resource | DaemonSet              | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 624 | CKV_K8S_111 | resource | Deployment             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 625 | CKV_K8S_111 | resource | Job                    | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 626 | CKV_K8S_111 | resource | Pod                    | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 627 | CKV_K8S_111 | resource | PodTemplate            | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 628 | CKV_K8S_111 | resource | ReplicaSet             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 629 | CKV_K8S_111 | resource | ReplicationController  | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 630 | CKV_K8S_111 | resource | StatefulSet            | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 631 | CKV_K8S_112 | resource | CronJob                | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 632 | CKV_K8S_112 | resource | DaemonSet              | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 633 | CKV_K8S_112 | resource | Deployment             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 634 | CKV_K8S_112 | resource | Job                    | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 635 | CKV_K8S_112 | resource | Pod                    | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 636 | CKV_K8S_112 | resource | PodTemplate            | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 637 | CKV_K8S_112 | resource | ReplicaSet             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 638 | CKV_K8S_112 | resource | ReplicationController  | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 639 | CKV_K8S_112 | resource | StatefulSet            | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 640 | CKV_K8S_113 | resource | CronJob                | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 641 | CKV_K8S_113 | resource | DaemonSet              | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 642 | CKV_K8S_113 | resource | Deployment             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 643 | CKV_K8S_113 | resource | Job                    | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 644 | CKV_K8S_113 | resource | Pod                    | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 645 | CKV_K8S_113 | resource | PodTemplate            | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 646 | CKV_K8S_113 | resource | ReplicaSet             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 647 | CKV_K8S_113 | resource | ReplicationController  | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 648 | CKV_K8S_113 | resource | StatefulSet            | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 649 | CKV_K8S_114 | resource | CronJob                | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 650 | CKV_K8S_114 | resource | DaemonSet              | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 651 | CKV_K8S_114 | resource | Deployment             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 652 | CKV_K8S_114 | resource | Job                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 653 | CKV_K8S_114 | resource | Pod                    | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 654 | CKV_K8S_114 | resource | PodTemplate            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 655 | CKV_K8S_114 | resource | ReplicaSet             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 656 | CKV_K8S_114 | resource | ReplicationController  | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 657 | CKV_K8S_114 | resource | StatefulSet            | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 658 | CKV_K8S_115 | resource | CronJob                | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 659 | CKV_K8S_115 | resource | DaemonSet              | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 660 | CKV_K8S_115 | resource | Deployment             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 661 | CKV_K8S_115 | resource | Job                    | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 662 | CKV_K8S_115 | resource | Pod                    | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 663 | CKV_K8S_115 | resource | PodTemplate            | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 664 | CKV_K8S_115 | resource | ReplicaSet             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 665 | CKV_K8S_115 | resource | ReplicationController  | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 666 | CKV_K8S_115 | resource | StatefulSet            | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 667 | CKV_K8S_116 | resource | CronJob                | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 668 | CKV_K8S_116 | resource | DaemonSet              | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 669 | CKV_K8S_116 | resource | Deployment             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 670 | CKV_K8S_116 | resource | Job                    | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 671 | CKV_K8S_116 | resource | Pod                    | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 672 | CKV_K8S_116 | resource | PodTemplate            | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 673 | CKV_K8S_116 | resource | ReplicaSet             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 674 | CKV_K8S_116 | resource | ReplicationController  | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 675 | CKV_K8S_116 | resource | StatefulSet            | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 676 | CKV_K8S_117 | resource | CronJob                | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 677 | CKV_K8S_117 | resource | DaemonSet              | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 678 | CKV_K8S_117 | resource | Deployment             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 679 | CKV_K8S_117 | resource | Job                    | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 680 | CKV_K8S_117 | resource | Pod                    | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 681 | CKV_K8S_117 | resource | PodTemplate            | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 682 | CKV_K8S_117 | resource | ReplicaSet             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 683 | CKV_K8S_117 | resource | ReplicationController  | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 684 | CKV_K8S_117 | resource | StatefulSet            | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 685 | CKV_K8S_118 | resource | CronJob                | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 686 | CKV_K8S_118 | resource | DaemonSet              | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 687 | CKV_K8S_118 | resource | Deployment             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 688 | CKV_K8S_118 | resource | Job                    | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 689 | CKV_K8S_118 | resource | Pod                    | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 690 | CKV_K8S_118 | resource | PodTemplate            | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 691 | CKV_K8S_118 | resource | ReplicaSet             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 692 | CKV_K8S_118 | resource | ReplicationController  | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 693 | CKV_K8S_118 | resource | StatefulSet            | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 694 | CKV_K8S_119 | resource | CronJob                | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 695 | CKV_K8S_119 | resource | DaemonSet              | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 696 | CKV_K8S_119 | resource | Deployment             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 697 | CKV_K8S_119 | resource | Job                    | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 698 | CKV_K8S_119 | resource | Pod                    | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 699 | CKV_K8S_119 | resource | PodTemplate            | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 700 | CKV_K8S_119 | resource | ReplicaSet             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 701 | CKV_K8S_119 | resource | ReplicationController  | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 702 | CKV_K8S_119 | resource | StatefulSet            | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 703 | CKV_K8S_121 | resource | Pod                    | Ensure that the --peer-client-cert-auth argument is set to true                                        | Kubernetes |
| 704 | CKV_K8S_138 | resource | CronJob                | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 705 | CKV_K8S_138 | resource | DaemonSet              | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 706 | CKV_K8S_138 | resource | Deployment             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 707 | CKV_K8S_138 | resource | Job                    | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 708 | CKV_K8S_138 | resource | Pod                    | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 709 | CKV_K8S_138 | resource | PodTemplate            | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 710 | CKV_K8S_138 | resource | ReplicaSet             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 711 | CKV_K8S_138 | resource | ReplicationController  | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 712 | CKV_K8S_138 | resource | StatefulSet            | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 713 | CKV_K8S_139 | resource | CronJob                | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 714 | CKV_K8S_139 | resource | DaemonSet              | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 715 | CKV_K8S_139 | resource | Deployment             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 716 | CKV_K8S_139 | resource | Job                    | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 717 | CKV_K8S_139 | resource | Pod                    | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 718 | CKV_K8S_139 | resource | PodTemplate            | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 719 | CKV_K8S_139 | resource | ReplicaSet             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 720 | CKV_K8S_139 | resource | ReplicationController  | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 721 | CKV_K8S_139 | resource | StatefulSet            | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 722 | CKV_K8S_140 | resource | CronJob                | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 723 | CKV_K8S_140 | resource | DaemonSet              | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 724 | CKV_K8S_140 | resource | Deployment             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 725 | CKV_K8S_140 | resource | Job                    | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 726 | CKV_K8S_140 | resource | Pod                    | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 727 | CKV_K8S_140 | resource | PodTemplate            | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 728 | CKV_K8S_140 | resource | ReplicaSet             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 729 | CKV_K8S_140 | resource | ReplicationController  | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 730 | CKV_K8S_140 | resource | StatefulSet            | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 731 | CKV_K8S_141 | resource | CronJob                | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 732 | CKV_K8S_141 | resource | DaemonSet              | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 733 | CKV_K8S_141 | resource | Deployment             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 734 | CKV_K8S_141 | resource | Job                    | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 735 | CKV_K8S_141 | resource | Pod                    | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 736 | CKV_K8S_141 | resource | PodTemplate            | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 737 | CKV_K8S_141 | resource | ReplicaSet             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 738 | CKV_K8S_141 | resource | ReplicationController  | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 739 | CKV_K8S_141 | resource | StatefulSet            | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 740 | CKV_K8S_143 | resource | CronJob                | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 741 | CKV_K8S_143 | resource | DaemonSet              | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 742 | CKV_K8S_143 | resource | Deployment             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 743 | CKV_K8S_143 | resource | Job                    | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 744 | CKV_K8S_143 | resource | Pod                    | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 745 | CKV_K8S_143 | resource | PodTemplate            | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 746 | CKV_K8S_143 | resource | ReplicaSet             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 747 | CKV_K8S_143 | resource | ReplicationController  | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 748 | CKV_K8S_143 | resource | StatefulSet            | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 749 | CKV_K8S_144 | resource | CronJob                | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 750 | CKV_K8S_144 | resource | DaemonSet              | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 751 | CKV_K8S_144 | resource | Deployment             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 752 | CKV_K8S_144 | resource | Job                    | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 753 | CKV_K8S_144 | resource | Pod                    | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 754 | CKV_K8S_144 | resource | PodTemplate            | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 755 | CKV_K8S_144 | resource | ReplicaSet             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 756 | CKV_K8S_144 | resource | ReplicationController  | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 757 | CKV_K8S_144 | resource | StatefulSet            | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 758 | CKV_K8S_145 | resource | CronJob                | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 759 | CKV_K8S_145 | resource | DaemonSet              | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 760 | CKV_K8S_145 | resource | Deployment             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 761 | CKV_K8S_145 | resource | Job                    | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 762 | CKV_K8S_145 | resource | Pod                    | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 763 | CKV_K8S_145 | resource | PodTemplate            | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 764 | CKV_K8S_145 | resource | ReplicaSet             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 765 | CKV_K8S_145 | resource | ReplicationController  | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 766 | CKV_K8S_145 | resource | StatefulSet            | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 767 | CKV_K8S_146 | resource | CronJob                | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 768 | CKV_K8S_146 | resource | DaemonSet              | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 769 | CKV_K8S_146 | resource | Deployment             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 770 | CKV_K8S_146 | resource | Job                    | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 771 | CKV_K8S_146 | resource | Pod                    | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 772 | CKV_K8S_146 | resource | PodTemplate            | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 773 | CKV_K8S_146 | resource | ReplicaSet             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 774 | CKV_K8S_146 | resource | ReplicationController  | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 775 | CKV_K8S_146 | resource | StatefulSet            | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 776 | CKV_K8S_147 | resource | CronJob                | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 777 | CKV_K8S_147 | resource | DaemonSet              | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 778 | CKV_K8S_147 | resource | Deployment             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 779 | CKV_K8S_147 | resource | Job                    | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 780 | CKV_K8S_147 | resource | Pod                    | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 781 | CKV_K8S_147 | resource | PodTemplate            | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 782 | CKV_K8S_147 | resource | ReplicaSet             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 783 | CKV_K8S_147 | resource | ReplicationController  | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 784 | CKV_K8S_147 | resource | StatefulSet            | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 785 | CKV_K8S_148 | resource | CronJob                | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 786 | CKV_K8S_148 | resource | DaemonSet              | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 787 | CKV_K8S_148 | resource | Deployment             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 788 | CKV_K8S_148 | resource | Job                    | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 789 | CKV_K8S_148 | resource | Pod                    | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 790 | CKV_K8S_148 | resource | PodTemplate            | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 791 | CKV_K8S_148 | resource | ReplicaSet             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 792 | CKV_K8S_148 | resource | ReplicationController  | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 793 | CKV_K8S_148 | resource | StatefulSet            | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 794 | CKV_K8S_149 | resource | CronJob                | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 795 | CKV_K8S_149 | resource | DaemonSet              | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 796 | CKV_K8S_149 | resource | Deployment             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 797 | CKV_K8S_149 | resource | Job                    | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 798 | CKV_K8S_149 | resource | Pod                    | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 799 | CKV_K8S_149 | resource | PodTemplate            | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 800 | CKV_K8S_149 | resource | ReplicaSet             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 801 | CKV_K8S_149 | resource | ReplicationController  | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 802 | CKV_K8S_149 | resource | StatefulSet            | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 803 | CKV_K8S_151 | resource | CronJob                | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 804 | CKV_K8S_151 | resource | DaemonSet              | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 805 | CKV_K8S_151 | resource | Deployment             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 806 | CKV_K8S_151 | resource | Job                    | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 807 | CKV_K8S_151 | resource | Pod                    | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 808 | CKV_K8S_151 | resource | PodTemplate            | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 809 | CKV_K8S_151 | resource | ReplicaSet             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 810 | CKV_K8S_151 | resource | ReplicationController  | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 811 | CKV_K8S_151 | resource | StatefulSet            | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 812 | CKV_K8S_152 | resource | Ingress                | Prevent NGINX Ingress annotation snippets which contain LUA code execution. See CVE-2021-25742         | Kubernetes |
| 813 | CKV_K8S_153 | resource | Ingress                | Prevent All NGINX Ingress annotation snippets. See CVE-2021-25742                                      | Kubernetes |
| 814 | CKV_K8S_154 | resource | Ingress                | Prevent NGINX Ingress annotation snippets which contain alias statements See CVE-2021-25742            | Kubernetes |


---


