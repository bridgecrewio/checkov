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
|   7 | CKV_K8S_8   | resource | containers             | Liveness Probe Should be Configured                                                                    | Kubernetes |
|   8 | CKV_K8S_9   | resource | containers             | Readiness Probe Should be Configured                                                                   | Kubernetes |
|   9 | CKV_K8S_10  | resource | containers             | CPU requests should be set                                                                             | Kubernetes |
|  10 | CKV_K8S_10  | resource | initContainers         | CPU requests should be set                                                                             | Kubernetes |
|  11 | CKV_K8S_11  | resource | containers             | CPU limits should be set                                                                               | Kubernetes |
|  12 | CKV_K8S_11  | resource | initContainers         | CPU limits should be set                                                                               | Kubernetes |
|  13 | CKV_K8S_12  | resource | containers             | Memory requests should be set                                                                          | Kubernetes |
|  14 | CKV_K8S_12  | resource | initContainers         | Memory requests should be set                                                                          | Kubernetes |
|  15 | CKV_K8S_13  | resource | containers             | Memory limits should be set                                                                            | Kubernetes |
|  16 | CKV_K8S_13  | resource | initContainers         | Memory limits should be set                                                                            | Kubernetes |
|  17 | CKV_K8S_14  | resource | containers             | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  18 | CKV_K8S_14  | resource | initContainers         | Image Tag should be fixed - not latest or blank                                                        | Kubernetes |
|  19 | CKV_K8S_15  | resource | containers             | Image Pull Policy should be Always                                                                     | Kubernetes |
|  20 | CKV_K8S_15  | resource | initContainers         | Image Pull Policy should be Always                                                                     | Kubernetes |
|  21 | CKV_K8S_16  | resource | containers             | Container should not be privileged                                                                     | Kubernetes |
|  22 | CKV_K8S_16  | resource | initContainers         | Container should not be privileged                                                                     | Kubernetes |
|  23 | CKV_K8S_17  | resource | Pod                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  24 | CKV_K8S_17  | resource | Deployment             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  25 | CKV_K8S_17  | resource | DaemonSet              | Containers should not share the host process ID namespace                                              | Kubernetes |
|  26 | CKV_K8S_17  | resource | StatefulSet            | Containers should not share the host process ID namespace                                              | Kubernetes |
|  27 | CKV_K8S_17  | resource | ReplicaSet             | Containers should not share the host process ID namespace                                              | Kubernetes |
|  28 | CKV_K8S_17  | resource | ReplicationController  | Containers should not share the host process ID namespace                                              | Kubernetes |
|  29 | CKV_K8S_17  | resource | Job                    | Containers should not share the host process ID namespace                                              | Kubernetes |
|  30 | CKV_K8S_17  | resource | CronJob                | Containers should not share the host process ID namespace                                              | Kubernetes |
|  31 | CKV_K8S_18  | resource | Pod                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  32 | CKV_K8S_18  | resource | Deployment             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  33 | CKV_K8S_18  | resource | DaemonSet              | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  34 | CKV_K8S_18  | resource | StatefulSet            | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  35 | CKV_K8S_18  | resource | ReplicaSet             | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  36 | CKV_K8S_18  | resource | ReplicationController  | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  37 | CKV_K8S_18  | resource | Job                    | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  38 | CKV_K8S_18  | resource | CronJob                | Containers should not share the host IPC namespace                                                     | Kubernetes |
|  39 | CKV_K8S_19  | resource | Pod                    | Containers should not share the host network namespace                                                 | Kubernetes |
|  40 | CKV_K8S_19  | resource | Deployment             | Containers should not share the host network namespace                                                 | Kubernetes |
|  41 | CKV_K8S_19  | resource | DaemonSet              | Containers should not share the host network namespace                                                 | Kubernetes |
|  42 | CKV_K8S_19  | resource | StatefulSet            | Containers should not share the host network namespace                                                 | Kubernetes |
|  43 | CKV_K8S_19  | resource | ReplicaSet             | Containers should not share the host network namespace                                                 | Kubernetes |
|  44 | CKV_K8S_19  | resource | ReplicationController  | Containers should not share the host network namespace                                                 | Kubernetes |
|  45 | CKV_K8S_19  | resource | Job                    | Containers should not share the host network namespace                                                 | Kubernetes |
|  46 | CKV_K8S_19  | resource | CronJob                | Containers should not share the host network namespace                                                 | Kubernetes |
|  47 | CKV_K8S_20  | resource | containers             | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|  48 | CKV_K8S_20  | resource | initContainers         | Containers should not run with allowPrivilegeEscalation                                                | Kubernetes |
|  49 | CKV_K8S_21  | resource | Service                | The default namespace should not be used                                                               | Kubernetes |
|  50 | CKV_K8S_21  | resource | Pod                    | The default namespace should not be used                                                               | Kubernetes |
|  51 | CKV_K8S_21  | resource | Deployment             | The default namespace should not be used                                                               | Kubernetes |
|  52 | CKV_K8S_21  | resource | DaemonSet              | The default namespace should not be used                                                               | Kubernetes |
|  53 | CKV_K8S_21  | resource | StatefulSet            | The default namespace should not be used                                                               | Kubernetes |
|  54 | CKV_K8S_21  | resource | ReplicaSet             | The default namespace should not be used                                                               | Kubernetes |
|  55 | CKV_K8S_21  | resource | ReplicationController  | The default namespace should not be used                                                               | Kubernetes |
|  56 | CKV_K8S_21  | resource | Job                    | The default namespace should not be used                                                               | Kubernetes |
|  57 | CKV_K8S_21  | resource | CronJob                | The default namespace should not be used                                                               | Kubernetes |
|  58 | CKV_K8S_21  | resource | Secret                 | The default namespace should not be used                                                               | Kubernetes |
|  59 | CKV_K8S_21  | resource | ServiceAccount         | The default namespace should not be used                                                               | Kubernetes |
|  60 | CKV_K8S_21  | resource | Role                   | The default namespace should not be used                                                               | Kubernetes |
|  61 | CKV_K8S_21  | resource | RoleBinding            | The default namespace should not be used                                                               | Kubernetes |
|  62 | CKV_K8S_21  | resource | ConfigMap              | The default namespace should not be used                                                               | Kubernetes |
|  63 | CKV_K8S_21  | resource | Ingress                | The default namespace should not be used                                                               | Kubernetes |
|  64 | CKV_K8S_22  | resource | containers             | Use read-only filesystem for containers where possible                                                 | Kubernetes |
|  65 | CKV_K8S_22  | resource | initContainers         | Use read-only filesystem for containers where possible                                                 | Kubernetes |
|  66 | CKV_K8S_23  | resource | Pod                    | Minimize the admission of root containers                                                              | Kubernetes |
|  67 | CKV_K8S_23  | resource | Deployment             | Minimize the admission of root containers                                                              | Kubernetes |
|  68 | CKV_K8S_23  | resource | DaemonSet              | Minimize the admission of root containers                                                              | Kubernetes |
|  69 | CKV_K8S_23  | resource | StatefulSet            | Minimize the admission of root containers                                                              | Kubernetes |
|  70 | CKV_K8S_23  | resource | ReplicaSet             | Minimize the admission of root containers                                                              | Kubernetes |
|  71 | CKV_K8S_23  | resource | ReplicationController  | Minimize the admission of root containers                                                              | Kubernetes |
|  72 | CKV_K8S_23  | resource | Job                    | Minimize the admission of root containers                                                              | Kubernetes |
|  73 | CKV_K8S_23  | resource | CronJob                | Minimize the admission of root containers                                                              | Kubernetes |
|  74 | CKV_K8S_24  | resource | PodSecurityPolicy      | Do not allow containers with added capability                                                          | Kubernetes |
|  75 | CKV_K8S_25  | resource | containers             | Minimize the admission of containers with added capability                                             | Kubernetes |
|  76 | CKV_K8S_25  | resource | initContainers         | Minimize the admission of containers with added capability                                             | Kubernetes |
|  77 | CKV_K8S_26  | resource | containers             | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
|  78 | CKV_K8S_26  | resource | initContainers         | Do not specify hostPort unless absolutely necessary                                                    | Kubernetes |
|  79 | CKV_K8S_27  | resource | Pod                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  80 | CKV_K8S_27  | resource | Deployment             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  81 | CKV_K8S_27  | resource | DaemonSet              | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  82 | CKV_K8S_27  | resource | StatefulSet            | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  83 | CKV_K8S_27  | resource | ReplicaSet             | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  84 | CKV_K8S_27  | resource | ReplicationController  | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  85 | CKV_K8S_27  | resource | Job                    | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  86 | CKV_K8S_27  | resource | CronJob                | Do not expose the docker daemon socket to containers                                                   | Kubernetes |
|  87 | CKV_K8S_28  | resource | containers             | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
|  88 | CKV_K8S_28  | resource | initContainers         | Minimize the admission of containers with the NET_RAW capability                                       | Kubernetes |
|  89 | CKV_K8S_29  | resource | Pod                    | Apply security context to your pods and containers                                                     | Kubernetes |
|  90 | CKV_K8S_29  | resource | Deployment             | Apply security context to your pods and containers                                                     | Kubernetes |
|  91 | CKV_K8S_29  | resource | DaemonSet              | Apply security context to your pods and containers                                                     | Kubernetes |
|  92 | CKV_K8S_29  | resource | StatefulSet            | Apply security context to your pods and containers                                                     | Kubernetes |
|  93 | CKV_K8S_29  | resource | ReplicaSet             | Apply security context to your pods and containers                                                     | Kubernetes |
|  94 | CKV_K8S_29  | resource | ReplicationController  | Apply security context to your pods and containers                                                     | Kubernetes |
|  95 | CKV_K8S_29  | resource | Job                    | Apply security context to your pods and containers                                                     | Kubernetes |
|  96 | CKV_K8S_29  | resource | CronJob                | Apply security context to your pods and containers                                                     | Kubernetes |
|  97 | CKV_K8S_30  | resource | containers             | Apply security context to your pods and containers                                                     | Kubernetes |
|  98 | CKV_K8S_30  | resource | initContainers         | Apply security context to your pods and containers                                                     | Kubernetes |
|  99 | CKV_K8S_31  | resource | Pod                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 100 | CKV_K8S_31  | resource | Deployment             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 101 | CKV_K8S_31  | resource | DaemonSet              | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 102 | CKV_K8S_31  | resource | StatefulSet            | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 103 | CKV_K8S_31  | resource | ReplicaSet             | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 104 | CKV_K8S_31  | resource | ReplicationController  | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 105 | CKV_K8S_31  | resource | Job                    | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 106 | CKV_K8S_31  | resource | CronJob                | Ensure that the seccomp profile is set to docker/default or runtime/default                            | Kubernetes |
| 107 | CKV_K8S_32  | resource | PodSecurityPolicy      | Ensure default seccomp profile set to docker/default or runtime/default                                | Kubernetes |
| 108 | CKV_K8S_33  | resource | containers             | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 109 | CKV_K8S_33  | resource | initContainers         | Ensure the Kubernetes dashboard is not deployed                                                        | Kubernetes |
| 110 | CKV_K8S_34  | resource | containers             | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 111 | CKV_K8S_34  | resource | initContainers         | Ensure that Tiller (Helm v2) is not deployed                                                           | Kubernetes |
| 112 | CKV_K8S_35  | resource | containers             | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 113 | CKV_K8S_35  | resource | initContainers         | Prefer using secrets as files over secrets as environment variables                                    | Kubernetes |
| 114 | CKV_K8S_36  | resource | PodSecurityPolicy      | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 115 | CKV_K8S_37  | resource | containers             | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 116 | CKV_K8S_37  | resource | initContainers         | Minimize the admission of containers with capabilities assigned                                        | Kubernetes |
| 117 | CKV_K8S_38  | resource | Pod                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 118 | CKV_K8S_38  | resource | Deployment             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 119 | CKV_K8S_38  | resource | DaemonSet              | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 120 | CKV_K8S_38  | resource | StatefulSet            | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 121 | CKV_K8S_38  | resource | ReplicaSet             | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 122 | CKV_K8S_38  | resource | ReplicationController  | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 123 | CKV_K8S_38  | resource | Job                    | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 124 | CKV_K8S_38  | resource | CronJob                | Ensure that Service Account Tokens are only mounted where necessary                                    | Kubernetes |
| 125 | CKV_K8S_39  | resource | containers             | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 126 | CKV_K8S_39  | resource | initContainers         | Do not use the CAP_SYS_ADMIN linux capability                                                          | Kubernetes |
| 127 | CKV_K8S_40  | resource | Pod                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 128 | CKV_K8S_40  | resource | Deployment             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 129 | CKV_K8S_40  | resource | DaemonSet              | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 130 | CKV_K8S_40  | resource | StatefulSet            | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 131 | CKV_K8S_40  | resource | ReplicaSet             | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 132 | CKV_K8S_40  | resource | ReplicationController  | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 133 | CKV_K8S_40  | resource | Job                    | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 134 | CKV_K8S_40  | resource | CronJob                | Containers should run as a high UID to avoid host conflict                                             | Kubernetes |
| 135 | CKV_K8S_41  | resource | ServiceAccount         | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 136 | CKV_K8S_42  | resource | RoleBinding            | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 137 | CKV_K8S_42  | resource | ClusterRoleBinding     | Ensure that default service accounts are not actively used                                             | Kubernetes |
| 138 | CKV_K8S_43  | resource | containers             | Image should use digest                                                                                | Kubernetes |
| 139 | CKV_K8S_43  | resource | initContainers         | Image should use digest                                                                                | Kubernetes |
| 140 | CKV_K8S_44  | resource | Service                | Ensure that the Tiller Service (Helm v2) is deleted                                                    | Kubernetes |
| 141 | CKV_K8S_45  | resource | containers             | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 142 | CKV_K8S_45  | resource | initContainers         | Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster                       | Kubernetes |
| 143 | CKV_K8S_49  | resource | Role                   | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 144 | CKV_K8S_49  | resource | ClusterRole            | Minimize wildcard use in Roles and ClusterRoles                                                        | Kubernetes |
| 145 | CKV_K8S_68  | resource | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 146 | CKV_K8S_69  | resource | containers             | Ensure that the --basic-auth-file argument is not set                                                  | Kubernetes |
| 147 | CKV_K8S_70  | resource | containers             | Ensure that the --token-auth-file argument is not set                                                  | Kubernetes |
| 148 | CKV_K8S_71  | resource | containers             | Ensure that the --kubelet-https argument is set to true                                                | Kubernetes |
| 149 | CKV_K8S_72  | resource | containers             | Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate | Kubernetes |
| 150 | CKV_K8S_73  | resource | containers             | Ensure that the --kubelet-certificate-authority argument is set as appropriate                         | Kubernetes |
| 151 | CKV_K8S_74  | resource | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 152 | CKV_K8S_75  | resource | containers             | Ensure that the --authorization-mode argument includes Node                                            | Kubernetes |
| 153 | CKV_K8S_77  | resource | containers             | Ensure that the --authorization-mode argument includes RBAC                                            | Kubernetes |
| 154 | CKV_K8S_78  | resource | AdmissionConfiguration | Ensure that the admission control plugin EventRateLimit is set                                         | Kubernetes |
| 155 | CKV_K8S_79  | resource | containers             | Ensure that the admission control plugin AlwaysAdmit is not set                                        | Kubernetes |
| 156 | CKV_K8S_80  | resource | containers             | Ensure that the admission control plugin AlwaysPullImages is set                                       | Kubernetes |
| 157 | CKV_K8S_81  | resource | containers             | Ensure that the admission control plugin SecurityContextDeny is set if PodSecurityPolicy is not used   | Kubernetes |
| 158 | CKV_K8S_82  | resource | containers             | Ensure that the admission control plugin ServiceAccount is set                                         | Kubernetes |
| 159 | CKV_K8S_83  | resource | containers             | Ensure that the admission control plugin NamespaceLifecycle is set                                     | Kubernetes |
| 160 | CKV_K8S_84  | resource | containers             | Ensure that the admission control plugin PodSecurityPolicy is set                                      | Kubernetes |
| 161 | CKV_K8S_85  | resource | containers             | Ensure that the admission control plugin NodeRestriction is set                                        | Kubernetes |
| 162 | CKV_K8S_86  | resource | containers             | Ensure that the --insecure-bind-address argument is not set                                            | Kubernetes |
| 163 | CKV_K8S_88  | resource | containers             | Ensure that the --insecure-port argument is set to 0                                                   | Kubernetes |
| 164 | CKV_K8S_89  | resource | containers             | Ensure that the --secure-port argument is not set to 0                                                 | Kubernetes |
| 165 | CKV_K8S_90  | resource | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 166 | CKV_K8S_91  | resource | containers             | Ensure that the --audit-log-path argument is set                                                       | Kubernetes |
| 167 | CKV_K8S_92  | resource | containers             | Ensure that the --audit-log-maxage argument is set to 30 or as appropriate                             | Kubernetes |
| 168 | CKV_K8S_93  | resource | containers             | Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate                          | Kubernetes |
| 169 | CKV_K8S_94  | resource | containers             | Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate                           | Kubernetes |
| 170 | CKV_K8S_95  | resource | containers             | Ensure that the --request-timeout argument is set as appropriate                                       | Kubernetes |
| 171 | CKV_K8S_96  | resource | containers             | Ensure that the --service-account-lookup argument is set to true                                       | Kubernetes |
| 172 | CKV_K8S_97  | resource | containers             | Ensure that the --service-account-key-file argument is set as appropriate                              | Kubernetes |
| 173 | CKV_K8S_99  | resource | containers             | Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate                    | Kubernetes |
| 174 | CKV_K8S_100 | resource | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 175 | CKV_K8S_102 | resource | containers             | Ensure that the --etcd-ca-file argument is set as appropriate                                          | Kubernetes |
| 176 | CKV_K8S_104 | resource | containers             | Ensure that encryption providers are appropriately configured                                          | Kubernetes |
| 177 | CKV_K8S_105 | resource | containers             | Ensure that the API Server only makes use of Strong Cryptographic Ciphers                              | Kubernetes |
| 178 | CKV_K8S_106 | resource | containers             | Ensure that the --terminated-pod-gc-threshold argument is set as appropriate                           | Kubernetes |
| 179 | CKV_K8S_107 | resource | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 180 | CKV_K8S_108 | resource | containers             | Ensure that the --use-service-account-credentials argument is set to true                              | Kubernetes |
| 181 | CKV_K8S_110 | resource | containers             | Ensure that the --service-account-private-key-file argument is set as appropriate                      | Kubernetes |
| 182 | CKV_K8S_111 | resource | containers             | Ensure that the --root-ca-file argument is set as appropriate                                          | Kubernetes |
| 183 | CKV_K8S_112 | resource | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 184 | CKV_K8S_113 | resource | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 185 | CKV_K8S_114 | resource | containers             | Ensure that the --profiling argument is set to false                                                   | Kubernetes |
| 186 | CKV_K8S_115 | resource | containers             | Ensure that the --bind-address argument is set to 127.0.0.1                                            | Kubernetes |
| 187 | CKV_K8S_116 | resource | containers             | Ensure that the --cert-file and --key-file arguments are set as appropriate                            | Kubernetes |
| 188 | CKV_K8S_117 | resource | containers             | Ensure that the --client-cert-auth argument is set to true                                             | Kubernetes |
| 189 | CKV_K8S_118 | resource | containers             | Ensure that the --auto-tls argument is not set to true                                                 | Kubernetes |
| 190 | CKV_K8S_119 | resource | containers             | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate                  | Kubernetes |
| 191 | CKV_K8S_121 | resource | Pod                    | Ensure that the --peer-client-cert-auth argument is set to true                                        | Kubernetes |
| 192 | CKV_K8S_138 | resource | containers             | Ensure that the --anonymous-auth argument is set to false                                              | Kubernetes |
| 193 | CKV_K8S_139 | resource | containers             | Ensure that the --authorization-mode argument is not set to AlwaysAllow                                | Kubernetes |
| 194 | CKV_K8S_140 | resource | containers             | Ensure that the --client-ca-file argument is set as appropriate                                        | Kubernetes |
| 195 | CKV_K8S_141 | resource | containers             | Ensure that the --read-only-port argument is set to 0                                                  | Kubernetes |
| 196 | CKV_K8S_143 | resource | containers             | Ensure that the --streaming-connection-idle-timeout argument is not set to 0                           | Kubernetes |
| 197 | CKV_K8S_144 | resource | containers             | Ensure that the --protect-kernel-defaults argument is set to true                                      | Kubernetes |
| 198 | CKV_K8S_145 | resource | containers             | Ensure that the --make-iptables-util-chains argument is set to true                                    | Kubernetes |
| 199 | CKV_K8S_146 | resource | containers             | Ensure that the --hostname-override argument is not set                                                | Kubernetes |
| 200 | CKV_K8S_147 | resource | containers             | Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture    | Kubernetes |
| 201 | CKV_K8S_148 | resource | containers             | Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate            | Kubernetes |
| 202 | CKV_K8S_149 | resource | containers             | Ensure that the --rotate-certificates argument is not set to false                                     | Kubernetes |
| 203 | CKV_K8S_150 | resource | containers             | Ensure that the RotateKubeletServerCertificate argument is set to true                                 | Kubernetes |
| 204 | CKV_K8S_151 | resource | containers             | Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers                                 | Kubernetes |


---


