variable "var_instance"{
  description = ""
  type = object({
          instance_name           = string
          instance_machine_type   = string
          instance_zone           = string
          instance_image          = string
          instance_interface_disk = string
          instance_network        = string
          meta_env                = string
    })
}

variable "path"{
  description = ""
  type = string
}
