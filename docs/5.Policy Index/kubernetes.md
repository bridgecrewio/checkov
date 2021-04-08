---
layout: default
title: kubernetes resource scans
nav_order: 1
---

# kubernetes resource scans (auto generated)

|     | Id          | Type                   | Entity                 | Policy                                                                                                 | IaC        |
|-----|-------------|------------------------|------------------------|--------------------------------------------------------------------------------------------------------|------------|
|   0 | CKV_K8S_1   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit containers wishing to share the host process ID namespace                                 | Kubernetes |
|   1 | CKV_K8S_1   | ClusterRole            | PodSecurityPolicy      | Do not admit containers wishing to share the host process ID namespace                                 | Kubernetes |
|   2 | CKV_K8S_1   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit containers wishing to share the host process ID namespace                                 | Kubernetes |
|   3 | CKV_K8S_2   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit privileged containers                                                                     | Kubernetes |
|   4 | CKV_K8S_2   | ClusterRole            | PodSecurityPolicy      | Do not admit privileged containers                                                                     | Kubernetes |
|   5 | CKV_K8S_2   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit privileged containers                                                                     | Kubernetes |
|   6 | CKV_K8S_3   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit containers wishing to share the host IPC namespace                                        | Kubernetes |
|   7 | CKV_K8S_3   | ClusterRole            | PodSecurityPolicy      | Do not admit containers wishing to share the host IPC namespace                                        | Kubernetes |
|   8 | CKV_K8S_3   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit containers wishing to share the host IPC namespace                                        | Kubernetes |
|   9 | CKV_K8S_4   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit containers wishing to share the host network namespace                                    | Kubernetes |
|  10 | CKV_K8S_4   | ClusterRole            | PodSecurityPolicy      | Do not admit containers wishing to share the host network namespace                                    | Kubernetes |
|  11 | CKV_K8S_4   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit containers wishing to share the host network namespace                                    | Kubernetes |
|  12 | CKV_K8S_5   | PodSecurityPolicy      | PodSecurityPolicy      | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|  13 | CKV_K8S_5   | ClusterRole            | PodSecurityPolicy      | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|  14 | CKV_K8S_5   | AdmissionConfiguration | PodSecurityPolicy      | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|  15 | CKV_K8S_6   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit root containers                                                                           | Kubernetes |
|  16 | CKV_K8S_6   | ClusterRole            | PodSecurityPolicy      | Do not admit root containers                                                                           | Kubernetes |
|  17 | CKV_K8S_6   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit root containers                                                                           | Kubernetes |
|  18 | CKV_K8S_7   | PodSecurityPolicy      | PodSecurityPolicy      | Do not admit containers with the NET_RAW capability                                                    | Kubernetes |
|  19 | CKV_K8S_7   | ClusterRole            | PodSecurityPolicy      | Do not admit containers with the NET_RAW capability                                                    | Kubernetes |
|  20 | CKV_K8S_7   | AdmissionConfiguration | PodSecurityPolicy      | Do not admit containers with the NET_RAW capability                                                    | Kubernetes |
|  21 | CKV_K8S_8   | PodSecurityPolicy      | containers             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  22 | CKV_K8S_8   | ClusterRole            | containers             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  23 | CKV_K8S_8   | AdmissionConfiguration | containers             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|  24 | CKV_K8S_9   | PodSecurityPolicy      | containers             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  25 | CKV_K8S_9   | ClusterRole            | containers             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  26 | CKV_K8S_9   | AdmissionConfiguration | containers             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|  27 | CKV_K8S_10  | PodSecurityPolicy      | containers             | CPU requests should be set                                                                             | Kubernetes |
|  28 | CKV_K8S_10  | PodSecurityPolicy      | initContainers         | CPU requests should be set                                                                             | Kubernetes |
|  29 | CKV_K8S_10  | ClusterRole            | containers             | CPU requests should be set                                                                             | Kubernetes |
|  30 | CKV_K8S_10  | ClusterRole            | initContainers         | CPU requests should be set                                                                             | Kubernetes |
|  31 | CKV_K8S_10  | AdmissionConfiguration | containers             | CPU requests should be set                                                                             | Kubernetes |
|  32 | CKV_K8S_10  | AdmissionConfiguration | initContainers         | CPU requests should be set                                                                             | Kubernetes |
|  33 | CKV_K8S_11  | PodSecurityPolicy      | containers             | CPU limits should be set                                                                               | Kubernetes |
|  34 | CKV_K8S_11  | PodSecurityPolicy      | initContainers         | CPU limits should be set                                                                               | Kubernetes |
|  35 | CKV_K8S_11  | ClusterRole            | containers             | CPU limits should be set                                                                               | Kubernetes |
|  36 | CKV_K8S_11  | ClusterRole            | initContainers         | CPU limits should be set                                                                               | Kubernetes |
|  37 | CKV_K8S_11  | AdmissionConfiguration | containers             | CPU limits should be set                                                                               | Kubernetes |
|  38 | CKV_K8S_11  | AdmissionConfiguration | initContainers         | CPU limits should be set                                                                               | Kubernetes |
|  39 | CKV_K8S_12  | PodSecurityPolicy      | containers             | Memory requests should be set                                                                          | Kubernetes |
|  40 | CKV_K8S_12  | PodSecurityPolicy      | initContainers         | Memory requests should be set                                                                          | Kubernetes |
|  41 | CKV_K8S_12  | ClusterRole            | containers             | Memory requests should be set                                                                          | Kubernetes |
|  42 | CKV_K8S_12  | ClusterRole            | initContainers         | Memory requests should be set                                                                          | Kubernetes |
|  43 | CKV_K8S_12  | AdmissionConfiguration | containers             | Memory requests should be set                                                                          | Kubernetes |
|  44 | CKV_K8S_12  | AdmissionConfiguration | initContainers         | Memory requests should be set                                                                          | Kubernetes |
|  45 | CKV_K8S_13  | PodSecurityPolicy      | containers             | Memory limits should be set                                                                            | Kubernetes |
|  46 | CKV_K8S_13  | PodSecurityPolicy      | initContainers         | Memory limits should be set                                                                            | Kubernetes |
|  47 | CKV_K8S_13  | ClusterRole            | containers             | Memory limits should be set                                                                            | Kubernetes |
|  48 | CKV_K8S_13  | ClusterRole            | initContainers         | Memory limits should be set                                                                            | Kubernetes |
|  49 | CKV_K8S_13  | AdmissionConfiguration | containers             | Memory limits should be set                                                                            | Kubernetes |
|  50 | CKV_K8S_13  | AdmissionConfiguration | initContainers         | Memory limits should be set                                                                            | Kubernetes |
|  51 | CKV_K8S_14  | PodSecurityPolicy      | containers             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  52 | CKV_K8S_14  | PodSecurityPolicy      | initContainers         | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  53 | CKV_K8S_14  | ClusterRole            | containers             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  54 | CKV_K8S_14  | ClusterRole            | initContainers         | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  55 | CKV_K8S_14  | AdmissionConfiguration | containers             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  56 | CKV_K8S_14  | AdmissionConfiguration | initContainers         | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  57 | CKV_K8S_15  | PodSecurityPolicy      | containers             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  58 | CKV_K8S_15  | PodSecurityPolicy      | initContainers         | Image Pull Policy should be Always                                                                     | Kubernetes |
|  59 | CKV_K8S_15  | ClusterRole            | containers             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  60 | CKV_K8S_15  | ClusterRole            | initContainers         | Image Pull Policy should be Always                                                                     | Kubernetes |
|  61 | CKV_K8S_15  | AdmissionConfiguration | containers             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  62 | CKV_K8S_15  | AdmissionConfiguration | initContainers         | Image Pull Policy should be Always                                                                     | Kubernetes |
|  63 | CKV_K8S_16  | PodSecurityPolicy      | containers             | Container should not be privileged                                                                     | Kubernetes |
|  64 | CKV_K8S_16  | PodSecurityPolicy      | initContainers         | Container should not be privileged                                                                     | Kubernetes |
|  65 | CKV_K8S_16  | ClusterRole            | containers             | Container should not be privileged                                                                     | Kubernetes |
|  66 | CKV_K8S_16  | ClusterRole            | initContainers         | Container should not be privileged                                                                     | Kubernetes |
|  67 | CKV_K8S_16  | AdmissionConfiguration | containers             | Container should not be privileged                                                                     | Kubernetes |
|  68 | CKV_K8S_16  | AdmissionConfiguration | initContainers         | Container should not be privileged                                                                     | Kubernetes |
|  69 | CKV_K8S_17  | PodSecurityPolicy      | Pod                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  70 | CKV_K8S_17  | PodSecurityPolicy      | Deployment             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  71 | CKV_K8S_17  | PodSecurityPolicy      | DaemonSet              | Containers should not share the host process ID namespace                                              | Kubernetes |
|  72 | CKV_K8S_17  | PodSecurityPolicy      | StatefulSet            | Containers should not share the host process ID namespace                                              | Kubernetes |
|  73 | CKV_K8S_17  | PodSecurityPolicy      | ReplicaSet             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  74 | CKV_K8S_17  | PodSecurityPolicy      | ReplicationController  | Containers should not share the host process ID namespace                                              | Kubernetes |
|  75 | CKV_K8S_17  | PodSecurityPolicy      | Job                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  76 | CKV_K8S_17  | PodSecurityPolicy      | CronJob                | Containers should not share the host process ID namespace                                              | Kubernetes |
|  77 | CKV_K8S_17  | ClusterRole            | Pod                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  78 | CKV_K8S_17  | ClusterRole            | Deployment             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  79 | CKV_K8S_17  | ClusterRole            | DaemonSet              | Containers should not share the host process ID namespace                                              | Kubernetes |
|  80 | CKV_K8S_17  | ClusterRole            | StatefulSet            | Containers should not share the host process ID namespace                                              | Kubernetes |
|  81 | CKV_K8S_17  | ClusterRole            | ReplicaSet             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  82 | CKV_K8S_17  | ClusterRole            | ReplicationController  | Containers should not share the host process ID namespace                                              | Kubernetes |
|  83 | CKV_K8S_17  | ClusterRole            | Job                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  84 | CKV_K8S_17  | ClusterRole            | CronJob                | Containers should not share the host process ID namespace                                              | Kubernetes |
|  85 | CKV_K8S_17  | AdmissionConfiguration | Pod                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  86 | CKV_K8S_17  | AdmissionConfiguration | Deployment             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  87 | CKV_K8S_17  | AdmissionConfiguration | DaemonSet              | Containers should not share the host process ID namespace                                              | Kubernetes |
|  88 | CKV_K8S_17  | AdmissionConfiguration | StatefulSet            | Containers should not share the host process ID namespace                                              | Kubernetes |
|  89 | CKV_K8S_17  | AdmissionConfiguration | ReplicaSet             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  90 | CKV_K8S_17  | AdmissionConfiguration | ReplicationController  | Containers should not share the host process ID namespace                                              | Kubernetes |
|  91 | CKV_K8S_17  | AdmissionConfiguration | Job                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  92 | CKV_K8S_17  | AdmissionConfiguration | CronJob                | Containers should not share the host process ID namespace                                              | Kubernetes |
|  93 | CKV_K8S_18  | PodSecurityPolicy      | Pod                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  94 | CKV_K8S_18  | PodSecurityPolicy      | Deployment             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  95 | CKV_K8S_18  | PodSecurityPolicy      | DaemonSet              | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  96 | CKV_K8S_18  | PodSecurityPolicy      | StatefulSet            | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  97 | CKV_K8S_18  | PodSecurityPolicy      | ReplicaSet             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  98 | CKV_K8S_18  | PodSecurityPolicy      | ReplicationController  | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  99 | CKV_K8S_18  | PodSecurityPolicy      | Job                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 100 | CKV_K8S_18  | PodSecurityPolicy      | CronJob                | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 101 | CKV_K8S_18  | ClusterRole            | Pod                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 102 | CKV_K8S_18  | ClusterRole            | Deployment             | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 103 | CKV_K8S_18  | ClusterRole            | DaemonSet              | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 104 | CKV_K8S_18  | ClusterRole            | StatefulSet            | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 105 | CKV_K8S_18  | ClusterRole            | ReplicaSet             | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 106 | CKV_K8S_18  | ClusterRole            | ReplicationController  | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 107 | CKV_K8S_18  | ClusterRole            | Job                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 108 | CKV_K8S_18  | ClusterRole            | CronJob                | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 109 | CKV_K8S_18  | AdmissionConfiguration | Pod                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 110 | CKV_K8S_18  | AdmissionConfiguration | Deployment             | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 111 | CKV_K8S_18  | AdmissionConfiguration | DaemonSet              | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 112 | CKV_K8S_18  | AdmissionConfiguration | StatefulSet            | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 113 | CKV_K8S_18  | AdmissionConfiguration | ReplicaSet             | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 114 | CKV_K8S_18  | AdmissionConfiguration | ReplicationController  | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 115 | CKV_K8S_18  | AdmissionConfiguration | Job                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 116 | CKV_K8S_18  | AdmissionConfiguration | CronJob                | Containers should not share the host IPC namespace                                                     | Kubernetes |
| 117 | CKV_K8S_19  | PodSecurityPolicy      | Pod                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 118 | CKV_K8S_19  | PodSecurityPolicy      | Deployment             | Containers should not share the host network namespace                                                 | Kubernetes |
| 119 | CKV_K8S_19  | PodSecurityPolicy      | DaemonSet              | Containers should not share the host network namespace                                                 | Kubernetes |
| 120 | CKV_K8S_19  | PodSecurityPolicy      | StatefulSet            | Containers should not share the host network namespace                                                 | Kubernetes |
| 121 | CKV_K8S_19  | PodSecurityPolicy      | ReplicaSet             | Containers should not share the host network namespace                                                 | Kubernetes |
| 122 | CKV_K8S_19  | PodSecurityPolicy      | ReplicationController  | Containers should not share the host network namespace                                                 | Kubernetes |
| 123 | CKV_K8S_19  | PodSecurityPolicy      | Job                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 124 | CKV_K8S_19  | PodSecurityPolicy      | CronJob                | Containers should not share the host network namespace                                                 | Kubernetes |
| 125 | CKV_K8S_19  | ClusterRole            | Pod                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 126 | CKV_K8S_19  | ClusterRole            | Deployment             | Containers should not share the host network namespace                                                 | Kubernetes |
| 127 | CKV_K8S_19  | ClusterRole            | DaemonSet              | Containers should not share the host network namespace                                                 | Kubernetes |
| 128 | CKV_K8S_19  | ClusterRole            | StatefulSet            | Containers should not share the host network namespace                                                 | Kubernetes |
| 129 | CKV_K8S_19  | ClusterRole            | ReplicaSet             | Containers should not share the host network namespace                                                 | Kubernetes |
| 130 | CKV_K8S_19  | ClusterRole            | ReplicationController  | Containers should not share the host network namespace                                                 | Kubernetes |
| 131 | CKV_K8S_19  | ClusterRole            | Job                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 132 | CKV_K8S_19  | ClusterRole            | CronJob                | Containers should not share the host network namespace                                                 | Kubernetes |
| 133 | CKV_K8S_19  | AdmissionConfiguration | Pod                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 134 | CKV_K8S_19  | AdmissionConfiguration | Deployment             | Containers should not share the host network namespace                                                 | Kubernetes |
| 135 | CKV_K8S_19  | AdmissionConfiguration | DaemonSet              | Containers should not share the host network namespace                                                 | Kubernetes |
| 136 | CKV_K8S_19  | AdmissionConfiguration | StatefulSet            | Containers should not share the host network namespace                                                 | Kubernetes |
| 137 | CKV_K8S_19  | AdmissionConfiguration | ReplicaSet             | Containers should not share the host network namespace                                                 | Kubernetes |
| 138 | CKV_K8S_19  | AdmissionConfiguration | ReplicationController  | Containers should not share the host network namespace                                                 | Kubernetes |
| 139 | CKV_K8S_19  | AdmissionConfiguration | Job                    | Containers should not share the host network namespace                                                 | Kubernetes |
| 140 | CKV_K8S_19  | AdmissionConfiguration | CronJob                | Containers should not share the host network namespace                                                 | Kubernetes |
| 141 | CKV_K8S_20  | PodSecurityPolicy      | containers             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 142 | CKV_K8S_20  | PodSecurityPolicy      | initContainers         | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 143 | CKV_K8S_20  | ClusterRole            | containers             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 144 | CKV_K8S_20  | ClusterRole            | initContainers         | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 145 | CKV_K8S_20  | AdmissionConfiguration | containers             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 146 | CKV_K8S_20  | AdmissionConfiguration | initContainers         | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
| 147 | CKV_K8S_21  | PodSecurityPolicy      | Service                | The default namespace should not be used                                                               | Kubernetes |
| 148 | CKV_K8S_21  | PodSecurityPolicy      | Pod                    | The default namespace should not be used                                                               | Kubernetes |
| 149 | CKV_K8S_21  | PodSecurityPolicy      | Deployment             | The default namespace should not be used                                                               | Kubernetes |
| 150 | CKV_K8S_21  | PodSecurityPolicy      | DaemonSet              | The default namespace should not be used                                                               | Kubernetes |
| 151 | CKV_K8S_21  | PodSecurityPolicy      | StatefulSet            | The default namespace should not be used                                                               | Kubernetes |
| 152 | CKV_K8S_21  | PodSecurityPolicy      | ReplicaSet             | The default namespace should not be used                                                               | Kubernetes |
| 153 | CKV_K8S_21  | PodSecurityPolicy      | ReplicationController  | The default namespace should not be used                                                               | Kubernetes |
| 154 | CKV_K8S_21  | PodSecurityPolicy      | Job                    | The default namespace should not be used                                                               | Kubernetes |
| 155 | CKV_K8S_21  | PodSecurityPolicy      | CronJob                | The default namespace should not be used                                                               | Kubernetes |
| 156 | CKV_K8S_21  | PodSecurityPolicy      | ServiceAccount         | The default namespace should not be used                                                               | Kubernetes |
| 157 | CKV_K8S_21  | PodSecurityPolicy      | Secret                 | The default namespace should not be used                                                               | Kubernetes |
| 158 | CKV_K8S_21  | PodSecurityPolicy      | Role                   | The default namespace should not be used                                                               | Kubernetes |
| 159 | CKV_K8S_21  | PodSecurityPolicy      | RoleBinding            | The default namespace should not be used                                                               | Kubernetes |
| 160 | CKV_K8S_21  | PodSecurityPolicy      | ConfigMap              | The default namespace should not be used                                                               | Kubernetes |
| 161 | CKV_K8S_21  | PodSecurityPolicy      | Ingress                | The default namespace should not be used                                                               | Kubernetes |
| 162 | CKV_K8S_21  | ClusterRole            | Service                | The default namespace should not be used                                                               | Kubernetes |
| 163 | CKV_K8S_21  | ClusterRole            | Pod                    | The default namespace should not be used                                                               | Kubernetes |
| 164 | CKV_K8S_21  | ClusterRole            | Deployment             | The default namespace should not be used                                                               | Kubernetes |
| 165 | CKV_K8S_21  | ClusterRole            | DaemonSet              | The default namespace should not be used                                                               | Kubernetes |
| 166 | CKV_K8S_21  | ClusterRole            | StatefulSet            | The default namespace should not be used                                                               | Kubernetes |
| 167 | CKV_K8S_21  | ClusterRole            | ReplicaSet             | The default namespace should not be used                                                               | Kubernetes |
| 168 | CKV_K8S_21  | ClusterRole            | ReplicationController  | The default namespace should not be used                                                               | Kubernetes |
| 169 | CKV_K8S_21  | ClusterRole            | Job                    | The default namespace should not be used                                                               | Kubernetes |
| 170 | CKV_K8S_21  | ClusterRole            | CronJob                | The default namespace should not be used                                                               | Kubernetes |
| 171 | CKV_K8S_21  | ClusterRole            | ServiceAccount         | The default namespace should not be used                                                               | Kubernetes |
| 172 | CKV_K8S_21  | ClusterRole            | Secret                 | The default namespace should not be used                                                               | Kubernetes |
| 173 | CKV_K8S_21  | ClusterRole            | Role                   | The default namespace should not be used                                                               | Kubernetes |
| 174 | CKV_K8S_21  | ClusterRole            | RoleBinding            | The default namespace should not be used                                                               | Kubernetes |
| 175 | CKV_K8S_21  | ClusterRole            | ConfigMap              | The default namespace should not be used                                                               | Kubernetes |
| 176 | CKV_K8S_21  | ClusterRole            | Ingress                | The default namespace should not be used                                                               | Kubernetes |
| 177 | CKV_K8S_21  | AdmissionConfiguration | Service                | The default namespace should not be used                                                               | Kubernetes |
| 178 | CKV_K8S_21  | AdmissionConfiguration | Pod                    | The default namespace should not be used                                                               | Kubernetes |
| 179 | CKV_K8S_21  | AdmissionConfiguration | Deployment             | The default namespace should not be used                                                               | Kubernetes |
| 180 | CKV_K8S_21  | AdmissionConfiguration | DaemonSet              | The default namespace should not be used                                                               | Kubernetes |
| 181 | CKV_K8S_21  | AdmissionConfiguration | StatefulSet            | The default namespace should not be used                                                               | Kubernetes |
| 182 | CKV_K8S_21  | AdmissionConfiguration | ReplicaSet             | The default namespace should not be used                                                               | Kubernetes |
| 183 | CKV_K8S_21  | AdmissionConfiguration | ReplicationController  | The default namespace should not be used                                                               | Kubernetes |
| 184 | CKV_K8S_21  | AdmissionConfiguration | Job                    | The default namespace should not be used                                                               | Kubernetes |
| 185 | CKV_K8S_21  | AdmissionConfiguration | CronJob                | The default namespace should not be used                                                               | Kubernetes |
| 186 | CKV_K8S_21  | AdmissionConfiguration | ServiceAccount         | The default namespace should not be used                                                               | Kubernetes |
| 187 | CKV_K8S_21  | AdmissionConfiguration | Secret                 | The default namespace should not be used                                                               | Kubernetes |
| 188 | CKV_K8S_21  | AdmissionConfiguration | Role                   | The default namespace should not be used                                                               | Kubernetes |
| 189 | CKV_K8S_21  | AdmissionConfiguration | RoleBinding            | The default namespace should not be used                                                               | Kubernetes |
| 190 | CKV_K8S_21  | AdmissionConfiguration | ConfigMap              | The default namespace should not be used                                                               | Kubernetes |
| 191 | CKV_K8S_21  | AdmissionConfiguration | Ingress                | The default namespace should not be used                                                               | Kubernetes |
| 192 | CKV_K8S_22  | PodSecurityPolicy      | containers             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 193 | CKV_K8S_22  | PodSecurityPolicy      | initContainers         | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 194 | CKV_K8S_22  | ClusterRole            | containers             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 195 | CKV_K8S_22  | ClusterRole            | initContainers         | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 196 | CKV_K8S_22  | AdmissionConfiguration | containers             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 197 | CKV_K8S_22  | AdmissionConfiguration | initContainers         | Use read-only filesystem for containers where possible                                                 | Kubernetes |
| 198 | CKV_K8S_23  | PodSecurityPolicy      | Pod                    | Minimize the admission of root containers                                                              | Kubernetes |
| 199 | CKV_K8S_23  | PodSecurityPolicy      | Deployment             | Minimize the admission of root containers                                                              | Kubernetes |
| 200 | CKV_K8S_23  | PodSecurityPolicy      | DaemonSet              | Minimize the admission of root containers                                                              | Kubernetes |
| 201 | CKV_K8S_23  | PodSecurityPolicy      | StatefulSet            | Minimize the admission of root containers                                                              | Kubernetes |
| 202 | CKV_K8S_23  | PodSecurityPolicy      | ReplicaSet             | Minimize the admission of root containers                                                              | Kubernetes |
| 203 | CKV_K8S_23  | PodSecurityPolicy      | ReplicationController  | Minimize the admission of root containers                                                              | Kubernetes |
| 204 | CKV_K8S_23  | PodSecurityPolicy      | Job                    | Minimize the admission of root containers                                                              | Kubernetes |
| 205 | CKV_K8S_23  | PodSecurityPolicy      | CronJob                | Minimize the admission of root containers                                                              | Kubernetes |
| 206 | CKV_K8S_23  | ClusterRole            | Pod                    | Minimize the admission of root containers                                                              | Kubernetes |
| 207 | CKV_K8S_23  | ClusterRole            | Deployment             | Minimize the admission of root containers                                                              | Kubernetes |
| 208 | CKV_K8S_23  | ClusterRole            | DaemonSet              | Minimize the admission of root containers                                                              | Kubernetes |
| 209 | CKV_K8S_23  | ClusterRole            | StatefulSet            | Minimize the admission of root containers                                                              | Kubernetes |
| 210 | CKV_K8S_23  | ClusterRole            | ReplicaSet             | Minimize the admission of root containers                                                              | Kubernetes |
| 211 | CKV_K8S_23  | ClusterRole            | ReplicationController  | Minimize the admission of root containers                                                              | Kubernetes |
| 212 | CKV_K8S_23  | ClusterRole            | Job                    | Minimize the admission of root containers                                                              | Kubernetes |
| 213 | CKV_K8S_23  | ClusterRole            | CronJob                | Minimize the admission of root containers                                                              | Kubernetes |
| 214 | CKV_K8S_23  | AdmissionConfiguration | Pod                    | Minimize the admission of root containers                                                              | Kubernetes |
| 215 | CKV_K8S_23  | AdmissionConfiguration | Deployment             | Minimize the admission of root containers                                                              | Kubernetes |
| 216 | CKV_K8S_23  | AdmissionConfiguration | DaemonSet              | Minimize the admission of root containers                                                              | Kubernetes |
| 217 | CKV_K8S_23  | AdmissionConfiguration | StatefulSet            | Minimize the admission of root containers                                                              | Kubernetes |
| 218 | CKV_K8S_23  | AdmissionConfiguration | ReplicaSet             | Minimize the admission of root containers                                                              | Kubernetes |
| 219 | CKV_K8S_23  | AdmissionConfiguration | ReplicationController  | Minimize the admission of root containers                                                              | Kubernetes |
| 220 | CKV_K8S_23  | AdmissionConfiguration | Job                    | Minimize the admission of root containers                                                              | Kubernetes |
| 221 | CKV_K8S_23  | AdmissionConfiguration | CronJob                | Minimize the admission of root containers                                                              | Kubernetes |
| 222 | CKV_K8S_24  | PodSecurityPolicy      | PodSecurityPolicy      | Do not allow containers with added capability                                                          | Kubernetes |
| 223 | CKV_K8S_24  | ClusterRole            | PodSecurityPolicy      | Do not allow containers with added capability                                                          | Kubernetes |
| 224 | CKV_K8S_24  | AdmissionConfiguration | PodSecurityPolicy      | Do not allow containers with added capability                                                          | Kubernetes |
| 225 | CKV_K8S_25  | PodSecurityPolicy      | containers             | Minimize the admission of containers with added capability                                             | Kubernetes |
| 226 | CKV_K8S_25  | PodSecurityPolicy      | initContainers         | Minimize the admission of containers with added capability                                             | Kubernetes |
| 227 | CKV_K8S_25  | ClusterRole            | containers             | Minimize the admission of containers with added capability                                             | Kubernetes |
| 228 | CKV_K8S_25  | ClusterRole            | initContainers         | Minimize the admission of containers with added capability                                             | Kubernetes |
| 229 | CKV_K8S_25  | AdmissionConfiguration | containers             | Minimize the admission of containers with added capability                                             | Kubernetes |
| 230 | CKV_K8S_25  | AdmissionConfiguration | initContainers         | Minimize the admission of containers with added capability                                             | Kubernetes |
| 231 | CKV_K8S_26  | PodSecurityPolicy      | containers             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 232 | CKV_K8S_26  | PodSecurityPolicy      | initContainers         | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 233 | CKV_K8S_26  | ClusterRole            | containers             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 234 | CKV_K8S_26  | ClusterRole            | initContainers         | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 235 | CKV_K8S_26  | AdmissionConfiguration | containers             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 236 | CKV_K8S_26  | AdmissionConfiguration | initContainers         | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
| 237 | CKV_K8S_27  | PodSecurityPolicy      | Pod                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 238 | CKV_K8S_27  | PodSecurityPolicy      | Deployment             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 239 | CKV_K8S_27  | PodSecurityPolicy      | DaemonSet              | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 240 | CKV_K8S_27  | PodSecurityPolicy      | StatefulSet            | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 241 | CKV_K8S_27  | PodSecurityPolicy      | ReplicaSet             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 242 | CKV_K8S_27  | PodSecurityPolicy      | ReplicationController  | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 243 | CKV_K8S_27  | PodSecurityPolicy      | Job                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 244 | CKV_K8S_27  | PodSecurityPolicy      | CronJob                | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 245 | CKV_K8S_27  | ClusterRole            | Pod                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 246 | CKV_K8S_27  | ClusterRole            | Deployment             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 247 | CKV_K8S_27  | ClusterRole            | DaemonSet              | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 248 | CKV_K8S_27  | ClusterRole            | StatefulSet            | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 249 | CKV_K8S_27  | ClusterRole            | ReplicaSet             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 250 | CKV_K8S_27  | ClusterRole            | ReplicationController  | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 251 | CKV_K8S_27  | ClusterRole            | Job                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 252 | CKV_K8S_27  | ClusterRole            | CronJob                | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 253 | CKV_K8S_27  | AdmissionConfiguration | Pod                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 254 | CKV_K8S_27  | AdmissionConfiguration | Deployment             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 255 | CKV_K8S_27  | AdmissionConfiguration | DaemonSet              | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 256 | CKV_K8S_27  | AdmissionConfiguration | StatefulSet            | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 257 | CKV_K8S_27  | AdmissionConfiguration | ReplicaSet             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 258 | CKV_K8S_27  | AdmissionConfiguration | ReplicationController  | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 259 | CKV_K8S_27  | AdmissionConfiguration | Job                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 260 | CKV_K8S_27  | AdmissionConfiguration | CronJob                | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
| 261 | CKV_K8S_28  | PodSecurityPolicy      | containers             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 262 | CKV_K8S_28  | PodSecurityPolicy      | initContainers         | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 263 | CKV_K8S_28  | ClusterRole            | containers             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 264 | CKV_K8S_28  | ClusterRole            | initContainers         | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 265 | CKV_K8S_28  | AdmissionConfiguration | containers             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 266 | CKV_K8S_28  | AdmissionConfiguration | initContainers         | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
| 267 | CKV_K8S_29  | PodSecurityPolicy      | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 268 | CKV_K8S_29  | PodSecurityPolicy      | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
| 269 | CKV_K8S_29  | PodSecurityPolicy      | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
| 270 | CKV_K8S_29  | PodSecurityPolicy      | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
| 271 | CKV_K8S_29  | PodSecurityPolicy      | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
| 272 | CKV_K8S_29  | PodSecurityPolicy      | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
| 273 | CKV_K8S_29  | PodSecurityPolicy      | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 274 | CKV_K8S_29  | PodSecurityPolicy      | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
| 275 | CKV_K8S_29  | ClusterRole            | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 276 | CKV_K8S_29  | ClusterRole            | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
| 277 | CKV_K8S_29  | ClusterRole            | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
| 278 | CKV_K8S_29  | ClusterRole            | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
| 279 | CKV_K8S_29  | ClusterRole            | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
| 280 | CKV_K8S_29  | ClusterRole            | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
| 281 | CKV_K8S_29  | ClusterRole            | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 282 | CKV_K8S_29  | ClusterRole            | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
| 283 | CKV_K8S_29  | AdmissionConfiguration | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 284 | CKV_K8S_29  | AdmissionConfiguration | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
| 285 | CKV_K8S_29  | AdmissionConfiguration | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
| 286 | CKV_K8S_29  | AdmissionConfiguration | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
| 287 | CKV_K8S_29  | AdmissionConfiguration | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
| 288 | CKV_K8S_29  | AdmissionConfiguration | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
| 289 | CKV_K8S_29  | AdmissionConfiguration | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
| 290 | CKV_K8S_29  | AdmissionConfiguration | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
| 291 | CKV_K8S_30  | PodSecurityPolicy      | containers             | Apply security context to your pods and containers                                                     | Kubernetes |
| 292 | CKV_K8S_30  | PodSecurityPolicy      | initContainers         | Apply security context to your pods and containers                                                     | Kubernetes |
| 293 | CKV_K8S_30  | ClusterRole            | containers             | Apply security context to your pods and containers                                                     | Kubernetes |
| 294 | CKV_K8S_30  | ClusterRole            | initContainers         | Apply security context to your pods and containers                                                     | Kubernetes |
| 295 | CKV_K8S_30  | AdmissionConfiguration | containers             | Apply security context to your pods and containers                                                     | Kubernetes |
| 296 | CKV_K8S_30  | AdmissionConfiguration | initContainers         | Apply security context to your pods and containers                                                     | Kubernetes |
| 297 | CKV_K8S_31  | PodSecurityPolicy      | Pod                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 298 | CKV_K8S_31  | PodSecurityPolicy      | Deployment             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 299 | CKV_K8S_31  | PodSecurityPolicy      | DaemonSet              | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 300 | CKV_K8S_31  | PodSecurityPolicy      | StatefulSet            | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 301 | CKV_K8S_31  | PodSecurityPolicy      | ReplicaSet             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 302 | CKV_K8S_31  | PodSecurityPolicy      | ReplicationController  | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 303 | CKV_K8S_31  | PodSecurityPolicy      | Job                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 304 | CKV_K8S_31  | PodSecurityPolicy      | CronJob                | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 305 | CKV_K8S_31  | ClusterRole            | Pod                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 306 | CKV_K8S_31  | ClusterRole            | Deployment             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 307 | CKV_K8S_31  | ClusterRole            | DaemonSet              | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 308 | CKV_K8S_31  | ClusterRole            | StatefulSet            | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 309 | CKV_K8S_31  | ClusterRole            | ReplicaSet             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 310 | CKV_K8S_31  | ClusterRole            | ReplicationController  | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 311 | CKV_K8S_31  | ClusterRole            | Job                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 312 | CKV_K8S_31  | ClusterRole            | CronJob                | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 313 | CKV_K8S_31  | AdmissionConfiguration | Pod                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 314 | CKV_K8S_31  | AdmissionConfiguration | Deployment             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 315 | CKV_K8S_31  | AdmissionConfiguration | DaemonSet              | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 316 | CKV_K8S_31  | AdmissionConfiguration | StatefulSet            | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 317 | CKV_K8S_31  | AdmissionConfiguration | ReplicaSet             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 318 | CKV_K8S_31  | AdmissionConfiguration | ReplicationController  | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 319 | CKV_K8S_31  | AdmissionConfiguration | Job                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 320 | CKV_K8S_31  | AdmissionConfiguration | CronJob                | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 321 | CKV_K8S_32  | PodSecurityPolicy      | PodSecurityPolicy      | Ensure default seccomp profile set to docker/default or runtime/default                                | Kubernetes |
| 322 | CKV_K8S_32  | ClusterRole            | PodSecurityPolicy      | Ensure default seccomp profile set to docker/default or runtime/default                                | Kubernetes |
| 323 | CKV_K8S_32  | AdmissionConfiguration | PodSecurityPolicy      | Ensure default seccomp profile set to docker/default or runtime/default                                | Kubernetes |
| 324 | CKV_K8S_33  | PodSecurityPolicy      | containers             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 325 | CKV_K8S_33  | PodSecurityPolicy      | initContainers         | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 326 | CKV_K8S_33  | ClusterRole            | containers             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 327 | CKV_K8S_33  | ClusterRole            | initContainers         | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 328 | CKV_K8S_33  | AdmissionConfiguration | containers             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 329 | CKV_K8S_33  | AdmissionConfiguration | initContainers         | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 330 | CKV_K8S_34  | PodSecurityPolicy      | containers             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 331 | CKV_K8S_34  | PodSecurityPolicy      | initContainers         | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 332 | CKV_K8S_34  | ClusterRole            | containers             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 333 | CKV_K8S_34  | ClusterRole            | initContainers         | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 334 | CKV_K8S_34  | AdmissionConfiguration | containers             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 335 | CKV_K8S_34  | AdmissionConfiguration | initContainers         | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 336 | CKV_K8S_35  | PodSecurityPolicy      | containers             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 337 | CKV_K8S_35  | PodSecurityPolicy      | initContainers         | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 338 | CKV_K8S_35  | ClusterRole            | containers             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 339 | CKV_K8S_35  | ClusterRole            | initContainers         | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 340 | CKV_K8S_35  | AdmissionConfiguration | containers             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 341 | CKV_K8S_35  | AdmissionConfiguration | initContainers         | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 342 | CKV_K8S_36  | PodSecurityPolicy      | PodSecurityPolicy      | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 343 | CKV_K8S_36  | ClusterRole            | PodSecurityPolicy      | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 344 | CKV_K8S_36  | AdmissionConfiguration | PodSecurityPolicy      | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 345 | CKV_K8S_37  | PodSecurityPolicy      | containers             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 346 | CKV_K8S_37  | PodSecurityPolicy      | initContainers         | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 347 | CKV_K8S_37  | ClusterRole            | containers             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 348 | CKV_K8S_37  | ClusterRole            | initContainers         | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 349 | CKV_K8S_37  | AdmissionConfiguration | containers             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 350 | CKV_K8S_37  | AdmissionConfiguration | initContainers         | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 351 | CKV_K8S_38  | PodSecurityPolicy      | Pod                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 352 | CKV_K8S_38  | PodSecurityPolicy      | Deployment             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 353 | CKV_K8S_38  | PodSecurityPolicy      | DaemonSet              | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 354 | CKV_K8S_38  | PodSecurityPolicy      | StatefulSet            | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 355 | CKV_K8S_38  | PodSecurityPolicy      | ReplicaSet             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 356 | CKV_K8S_38  | PodSecurityPolicy      | ReplicationController  | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 357 | CKV_K8S_38  | PodSecurityPolicy      | Job                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 358 | CKV_K8S_38  | PodSecurityPolicy      | CronJob                | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 359 | CKV_K8S_38  | ClusterRole            | Pod                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 360 | CKV_K8S_38  | ClusterRole            | Deployment             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 361 | CKV_K8S_38  | ClusterRole            | DaemonSet              | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 362 | CKV_K8S_38  | ClusterRole            | StatefulSet            | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 363 | CKV_K8S_38  | ClusterRole            | ReplicaSet             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 364 | CKV_K8S_38  | ClusterRole            | ReplicationController  | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 365 | CKV_K8S_38  | ClusterRole            | Job                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 366 | CKV_K8S_38  | ClusterRole            | CronJob                | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 367 | CKV_K8S_38  | AdmissionConfiguration | Pod                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 368 | CKV_K8S_38  | AdmissionConfiguration | Deployment             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 369 | CKV_K8S_38  | AdmissionConfiguration | DaemonSet              | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 370 | CKV_K8S_38  | AdmissionConfiguration | StatefulSet            | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 371 | CKV_K8S_38  | AdmissionConfiguration | ReplicaSet             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 372 | CKV_K8S_38  | AdmissionConfiguration | ReplicationController  | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 373 | CKV_K8S_38  | AdmissionConfiguration | Job                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 374 | CKV_K8S_38  | AdmissionConfiguration | CronJob                | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 375 | CKV_K8S_39  | PodSecurityPolicy      | containers             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 376 | CKV_K8S_39  | PodSecurityPolicy      | initContainers         | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 377 | CKV_K8S_39  | ClusterRole            | containers             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 378 | CKV_K8S_39  | ClusterRole            | initContainers         | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 379 | CKV_K8S_39  | AdmissionConfiguration | containers             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 380 | CKV_K8S_39  | AdmissionConfiguration | initContainers         | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 381 | CKV_K8S_40  | PodSecurityPolicy      | Pod                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 382 | CKV_K8S_40  | PodSecurityPolicy      | Deployment             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 383 | CKV_K8S_40  | PodSecurityPolicy      | DaemonSet              | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 384 | CKV_K8S_40  | PodSecurityPolicy      | StatefulSet            | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 385 | CKV_K8S_40  | PodSecurityPolicy      | ReplicaSet             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 386 | CKV_K8S_40  | PodSecurityPolicy      | ReplicationController  | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 387 | CKV_K8S_40  | PodSecurityPolicy      | Job                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 388 | CKV_K8S_40  | PodSecurityPolicy      | CronJob                | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 389 | CKV_K8S_40  | ClusterRole            | Pod                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 390 | CKV_K8S_40  | ClusterRole            | Deployment             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 391 | CKV_K8S_40  | ClusterRole            | DaemonSet              | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 392 | CKV_K8S_40  | ClusterRole            | StatefulSet            | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 393 | CKV_K8S_40  | ClusterRole            | ReplicaSet             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 394 | CKV_K8S_40  | ClusterRole            | ReplicationController  | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 395 | CKV_K8S_40  | ClusterRole            | Job                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 396 | CKV_K8S_40  | ClusterRole            | CronJob                | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 397 | CKV_K8S_40  | AdmissionConfiguration | Pod                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 398 | CKV_K8S_40  | AdmissionConfiguration | Deployment             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 399 | CKV_K8S_40  | AdmissionConfiguration | DaemonSet              | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 400 | CKV_K8S_40  | AdmissionConfiguration | StatefulSet            | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 401 | CKV_K8S_40  | AdmissionConfiguration | ReplicaSet             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 402 | CKV_K8S_40  | AdmissionConfiguration | ReplicationController  | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 403 | CKV_K8S_40  | AdmissionConfiguration | Job                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 404 | CKV_K8S_40  | AdmissionConfiguration | CronJob                | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 405 | CKV_K8S_41  | PodSecurityPolicy      | ServiceAccount         | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 406 | CKV_K8S_41  | ClusterRole            | ServiceAccount         | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 407 | CKV_K8S_41  | AdmissionConfiguration | ServiceAccount         | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 408 | CKV_K8S_42  | PodSecurityPolicy      | RoleBinding            | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 409 | CKV_K8S_42  | PodSecurityPolicy      | ClusterRoleBinding     | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 410 | CKV_K8S_42  | ClusterRole            | RoleBinding            | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 411 | CKV_K8S_42  | ClusterRole            | ClusterRoleBinding     | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 412 | CKV_K8S_42  | AdmissionConfiguration | RoleBinding            | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 413 | CKV_K8S_42  | AdmissionConfiguration | ClusterRoleBinding     | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 414 | CKV_K8S_43  | PodSecurityPolicy      | containers             | Image should use digest                                                                                | Kubernetes |
| 415 | CKV_K8S_43  | PodSecurityPolicy      | initContainers         | Image should use digest                                                                                | Kubernetes |
| 416 | CKV_K8S_43  | ClusterRole            | containers             | Image should use digest                                                                                | Kubernetes |
| 417 | CKV_K8S_43  | ClusterRole            | initContainers         | Image should use digest                                                                                | Kubernetes |
| 418 | CKV_K8S_43  | AdmissionConfiguration | containers             | Image should use digest                                                                                | Kubernetes |
| 419 | CKV_K8S_43  | AdmissionConfiguration | initContainers         | Image should use digest                                                                                | Kubernetes |
| 420 | CKV_K8S_44  | PodSecurityPolicy      | Service                | Ensure that the Tiller Service (Helm v2) is deleted                                                    | Kubernetes |
| 421 | CKV_K8S_44  | ClusterRole            | Service                | Ensure that the Tiller Service (Helm v2) is deleted                                                    | Kubernetes |
| 422 | CKV_K8S_44  | AdmissionConfiguration | Service                | Ensure that the Tiller Service (Helm v2) is deleted                                                    | Kubernetes |
| 423 | CKV_K8S_45  | PodSecurityPolicy      | containers             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 424 | CKV_K8S_45  | PodSecurityPolicy      | initContainers         | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 425 | CKV_K8S_45  | ClusterRole            | containers             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 426 | CKV_K8S_45  | ClusterRole            | initContainers         | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 427 | CKV_K8S_45  | AdmissionConfiguration | containers             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 428 | CKV_K8S_45  | AdmissionConfiguration | initContainers         | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 429 | CKV_K8S_49  | PodSecurityPolicy      | Role                   | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 430 | CKV_K8S_49  | PodSecurityPolicy      | ClusterRole            | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 431 | CKV_K8S_49  | ClusterRole            | Role                   | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 432 | CKV_K8S_49  | ClusterRole            | ClusterRole            | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 433 | CKV_K8S_49  | AdmissionConfiguration | Role                   | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 434 | CKV_K8S_49  | AdmissionConfiguration | ClusterRole            | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 435 | CKV_K8S_68  | PodSecurityPolicy      | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 436 | CKV_K8S_68  | ClusterRole            | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 437 | CKV_K8S_68  | AdmissionConfiguration | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 438 | CKV_K8S_69  | PodSecurityPolicy      | containers             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 439 | CKV_K8S_69  | ClusterRole            | containers             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 440 | CKV_K8S_69  | AdmissionConfiguration | containers             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 441 | CKV_K8S_70  | PodSecurityPolicy      | containers             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 442 | CKV_K8S_70  | ClusterRole            | containers             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 443 | CKV_K8S_70  | AdmissionConfiguration | containers             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 444 | CKV_K8S_71  | PodSecurityPolicy      | containers             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 445 | CKV_K8S_71  | ClusterRole            | containers             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 446 | CKV_K8S_71  | AdmissionConfiguration | containers             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 447 | CKV_K8S_72  | PodSecurityPolicy      | containers             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 448 | CKV_K8S_72  | ClusterRole            | containers             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 449 | CKV_K8S_72  | AdmissionConfiguration | containers             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 450 | CKV_K8S_73  | PodSecurityPolicy      | containers             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 451 | CKV_K8S_73  | ClusterRole            | containers             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 452 | CKV_K8S_73  | AdmissionConfiguration | containers             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 453 | CKV_K8S_74  | PodSecurityPolicy      | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 454 | CKV_K8S_74  | ClusterRole            | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 455 | CKV_K8S_74  | AdmissionConfiguration | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 456 | CKV_K8S_75  | PodSecurityPolicy      | containers             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 457 | CKV_K8S_75  | ClusterRole            | containers             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 458 | CKV_K8S_75  | AdmissionConfiguration | containers             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 459 | CKV_K8S_77  | PodSecurityPolicy      | containers             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 460 | CKV_K8S_77  | ClusterRole            | containers             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 461 | CKV_K8S_77  | AdmissionConfiguration | containers             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 462 | CKV_K8S_78  | PodSecurityPolicy      | AdmissionConfiguration | Ensure that the admission control plugin EventRateLimit is set                                         | Kubernetes |
| 463 | CKV_K8S_78  | ClusterRole            | AdmissionConfiguration | Ensure that the admission control plugin EventRateLimit is set                                         | Kubernetes |
| 464 | CKV_K8S_78  | AdmissionConfiguration | AdmissionConfiguration | Ensure that the admission control plugin EventRateLimit is set                                         | Kubernetes |
| 465 | CKV_K8S_79  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 466 | CKV_K8S_79  | ClusterRole            | containers             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 467 | CKV_K8S_79  | AdmissionConfiguration | containers             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 468 | CKV_K8S_80  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 469 | CKV_K8S_80  | ClusterRole            | containers             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 470 | CKV_K8S_80  | AdmissionConfiguration | containers             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 471 | CKV_K8S_81  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 472 | CKV_K8S_81  | ClusterRole            | containers             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 473 | CKV_K8S_81  | AdmissionConfiguration | containers             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 474 | CKV_K8S_82  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 475 | CKV_K8S_82  | ClusterRole            | containers             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 476 | CKV_K8S_82  | AdmissionConfiguration | containers             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 477 | CKV_K8S_83  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 478 | CKV_K8S_83  | ClusterRole            | containers             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 479 | CKV_K8S_83  | AdmissionConfiguration | containers             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 480 | CKV_K8S_84  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 481 | CKV_K8S_84  | ClusterRole            | containers             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 482 | CKV_K8S_84  | AdmissionConfiguration | containers             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 483 | CKV_K8S_85  | PodSecurityPolicy      | containers             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 484 | CKV_K8S_85  | ClusterRole            | containers             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 485 | CKV_K8S_85  | AdmissionConfiguration | containers             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 486 | CKV_K8S_86  | PodSecurityPolicy      | containers             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 487 | CKV_K8S_86  | ClusterRole            | containers             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 488 | CKV_K8S_86  | AdmissionConfiguration | containers             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 489 | CKV_K8S_88  | PodSecurityPolicy      | containers             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 490 | CKV_K8S_88  | ClusterRole            | containers             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 491 | CKV_K8S_88  | AdmissionConfiguration | containers             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 492 | CKV_K8S_89  | PodSecurityPolicy      | containers             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 493 | CKV_K8S_89  | ClusterRole            | containers             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 494 | CKV_K8S_89  | AdmissionConfiguration | containers             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 495 | CKV_K8S_90  | PodSecurityPolicy      | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 496 | CKV_K8S_90  | ClusterRole            | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 497 | CKV_K8S_90  | AdmissionConfiguration | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 498 | CKV_K8S_91  | PodSecurityPolicy      | containers             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 499 | CKV_K8S_91  | ClusterRole            | containers             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 500 | CKV_K8S_91  | AdmissionConfiguration | containers             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 501 | CKV_K8S_92  | PodSecurityPolicy      | containers             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 502 | CKV_K8S_92  | ClusterRole            | containers             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 503 | CKV_K8S_92  | AdmissionConfiguration | containers             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 504 | CKV_K8S_93  | PodSecurityPolicy      | containers             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 505 | CKV_K8S_93  | ClusterRole            | containers             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 506 | CKV_K8S_93  | AdmissionConfiguration | containers             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 507 | CKV_K8S_94  | PodSecurityPolicy      | containers             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 508 | CKV_K8S_94  | ClusterRole            | containers             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 509 | CKV_K8S_94  | AdmissionConfiguration | containers             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 510 | CKV_K8S_95  | PodSecurityPolicy      | containers             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 511 | CKV_K8S_95  | ClusterRole            | containers             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 512 | CKV_K8S_95  | AdmissionConfiguration | containers             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 513 | CKV_K8S_96  | PodSecurityPolicy      | containers             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 514 | CKV_K8S_96  | ClusterRole            | containers             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 515 | CKV_K8S_96  | AdmissionConfiguration | containers             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 516 | CKV_K8S_97  | PodSecurityPolicy      | containers             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 517 | CKV_K8S_97  | ClusterRole            | containers             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 518 | CKV_K8S_97  | AdmissionConfiguration | containers             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 519 | CKV_K8S_99  | PodSecurityPolicy      | containers             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 520 | CKV_K8S_99  | ClusterRole            | containers             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 521 | CKV_K8S_99  | AdmissionConfiguration | containers             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 522 | CKV_K8S_100 | PodSecurityPolicy      | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 523 | CKV_K8S_100 | ClusterRole            | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 524 | CKV_K8S_100 | AdmissionConfiguration | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 525 | CKV_K8S_102 | PodSecurityPolicy      | containers             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 526 | CKV_K8S_102 | ClusterRole            | containers             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 527 | CKV_K8S_102 | AdmissionConfiguration | containers             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 528 | CKV_K8S_104 | PodSecurityPolicy      | containers             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 529 | CKV_K8S_104 | ClusterRole            | containers             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 530 | CKV_K8S_104 | AdmissionConfiguration | containers             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 531 | CKV_K8S_105 | PodSecurityPolicy      | containers             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 532 | CKV_K8S_105 | ClusterRole            | containers             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 533 | CKV_K8S_105 | AdmissionConfiguration | containers             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 534 | CKV_K8S_106 | PodSecurityPolicy      | containers             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 535 | CKV_K8S_106 | ClusterRole            | containers             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 536 | CKV_K8S_106 | AdmissionConfiguration | containers             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 537 | CKV_K8S_107 | PodSecurityPolicy      | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 538 | CKV_K8S_107 | ClusterRole            | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 539 | CKV_K8S_107 | AdmissionConfiguration | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 540 | CKV_K8S_108 | PodSecurityPolicy      | containers             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 541 | CKV_K8S_108 | ClusterRole            | containers             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 542 | CKV_K8S_108 | AdmissionConfiguration | containers             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 543 | CKV_K8S_110 | PodSecurityPolicy      | containers             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 544 | CKV_K8S_110 | ClusterRole            | containers             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 545 | CKV_K8S_110 | AdmissionConfiguration | containers             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 546 | CKV_K8S_111 | PodSecurityPolicy      | containers             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 547 | CKV_K8S_111 | ClusterRole            | containers             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 548 | CKV_K8S_111 | AdmissionConfiguration | containers             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 549 | CKV_K8S_112 | PodSecurityPolicy      | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 550 | CKV_K8S_112 | ClusterRole            | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 551 | CKV_K8S_112 | AdmissionConfiguration | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 552 | CKV_K8S_113 | PodSecurityPolicy      | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 553 | CKV_K8S_113 | ClusterRole            | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 554 | CKV_K8S_113 | AdmissionConfiguration | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 555 | CKV_K8S_114 | PodSecurityPolicy      | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 556 | CKV_K8S_114 | ClusterRole            | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 557 | CKV_K8S_114 | AdmissionConfiguration | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 558 | CKV_K8S_115 | PodSecurityPolicy      | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 559 | CKV_K8S_115 | ClusterRole            | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 560 | CKV_K8S_115 | AdmissionConfiguration | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 561 | CKV_K8S_116 | PodSecurityPolicy      | containers             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 562 | CKV_K8S_116 | ClusterRole            | containers             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 563 | CKV_K8S_116 | AdmissionConfiguration | containers             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 564 | CKV_K8S_117 | PodSecurityPolicy      | containers             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 565 | CKV_K8S_117 | ClusterRole            | containers             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 566 | CKV_K8S_117 | AdmissionConfiguration | containers             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 567 | CKV_K8S_118 | PodSecurityPolicy      | containers             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 568 | CKV_K8S_118 | ClusterRole            | containers             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 569 | CKV_K8S_118 | AdmissionConfiguration | containers             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 570 | CKV_K8S_119 | PodSecurityPolicy      | containers             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 571 | CKV_K8S_119 | ClusterRole            | containers             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 572 | CKV_K8S_119 | AdmissionConfiguration | containers             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 573 | CKV_K8S_121 | PodSecurityPolicy      | Pod                    | Ensure that the --peer-client-cert-auth argument is set to true                                        | Kubernetes |
| 574 | CKV_K8S_121 | ClusterRole            | Pod                    | Ensure that the --peer-client-cert-auth argument is set to true                                        | Kubernetes |
| 575 | CKV_K8S_121 | AdmissionConfiguration | Pod                    | Ensure that the --peer-client-cert-auth argument is set to true                                        | Kubernetes |
| 576 | CKV_K8S_138 | PodSecurityPolicy      | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 577 | CKV_K8S_138 | ClusterRole            | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 578 | CKV_K8S_138 | AdmissionConfiguration | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 579 | CKV_K8S_139 | PodSecurityPolicy      | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 580 | CKV_K8S_139 | ClusterRole            | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 581 | CKV_K8S_139 | AdmissionConfiguration | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 582 | CKV_K8S_140 | PodSecurityPolicy      | containers             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 583 | CKV_K8S_140 | ClusterRole            | containers             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 584 | CKV_K8S_140 | AdmissionConfiguration | containers             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 585 | CKV_K8S_141 | PodSecurityPolicy      | containers             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 586 | CKV_K8S_141 | ClusterRole            | containers             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 587 | CKV_K8S_141 | AdmissionConfiguration | containers             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 588 | CKV_K8S_143 | PodSecurityPolicy      | containers             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 589 | CKV_K8S_143 | ClusterRole            | containers             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 590 | CKV_K8S_143 | AdmissionConfiguration | containers             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 591 | CKV_K8S_144 | PodSecurityPolicy      | containers             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 592 | CKV_K8S_144 | ClusterRole            | containers             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 593 | CKV_K8S_144 | AdmissionConfiguration | containers             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 594 | CKV_K8S_145 | PodSecurityPolicy      | containers             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 595 | CKV_K8S_145 | ClusterRole            | containers             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 596 | CKV_K8S_145 | AdmissionConfiguration | containers             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 597 | CKV_K8S_146 | PodSecurityPolicy      | containers             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 598 | CKV_K8S_146 | ClusterRole            | containers             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 599 | CKV_K8S_146 | AdmissionConfiguration | containers             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 600 | CKV_K8S_147 | PodSecurityPolicy      | containers             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 601 | CKV_K8S_147 | ClusterRole            | containers             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 602 | CKV_K8S_147 | AdmissionConfiguration | containers             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 603 | CKV_K8S_148 | PodSecurityPolicy      | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 604 | CKV_K8S_148 | ClusterRole            | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 605 | CKV_K8S_148 | AdmissionConfiguration | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 606 | CKV_K8S_149 | PodSecurityPolicy      | containers             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 607 | CKV_K8S_149 | ClusterRole            | containers             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 608 | CKV_K8S_149 | AdmissionConfiguration | containers             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 609 | CKV_K8S_150 | PodSecurityPolicy      | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 610 | CKV_K8S_150 | ClusterRole            | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 611 | CKV_K8S_150 | AdmissionConfiguration | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 612 | CKV_K8S_151 | PodSecurityPolicy      | containers             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 613 | CKV_K8S_151 | ClusterRole            | containers             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |
| 614 | CKV_K8S_151 | AdmissionConfiguration | containers             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |


---


