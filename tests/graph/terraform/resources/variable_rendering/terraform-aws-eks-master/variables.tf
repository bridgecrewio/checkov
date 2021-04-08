variable "region" {
  type        = string
  description = "AWS Region"
}

variable "access_key" {
  type        = string
  description = "AWS Access Key"
}

variable "secret_key" {
  type        = string
  description = "AWS Secret Key"
}

variable "project" {
  type = string
}

variable "cluster_name" {
  type        = string
  description = "EKS name"
}

variable "accessing_computer_ips" {
  type        = list(string)
  description = "cidr blocks"
}

variable "number_of_subnets" {
  type        = number
  default     = 2
  description = "Number of subnets"
}

variable "iam_worker_instance_profile_name" {
  type        = string
  default     = "ipaas-eks-workers"
  description = "IAM worker instance profile name"
}

variable "kubeconfig_path" {
  type        = string
  default     = "./kubeconfig"
  description = "Kubeconfig path"
}

variable "create_kubeconfig" {
  type        = bool
  default     = true
}

variable "kubernetes_version" {
  type        = string
  default     = "1.19"
  description = "EKS kubernetes version."
}

variable "node_groups" {
  type = list(object({
    name          = string
    desired_size  = number
    max_size      = number
    min_size      = number
    instance_type = string
    # Opcionais
    # ami_type  = string (Default: AL2_x86_64)
    # disk_size = number (Default: 20)
  }))
  default = [
    {
      name          = "example"
      desired_size  = 2
      max_size      = 3
      min_size      = 1
      instance_type = "t3.medium"
    }
  ]
}
