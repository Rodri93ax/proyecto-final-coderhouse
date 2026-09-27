variable "admin_cidr" {
  description = "IPv4 publica del administrador con mascara /32"
  type        = string

  validation {
    condition = (
      can(cidrnetmask(var.admin_cidr)) &&
      endswith(var.admin_cidr, "/32")
    )
    error_message = "Indicar una unica IPv4 publica con mascara /32."
  }
}

variable "public_key_path" {
  description = "Ruta a la clave SSH publica"
  type        = string
  default     = "~/.ssh/coderhouse-aws.pub"
}

variable "instance_type" {
  description = "Tipo de servidor del laboratorio"
  type        = string
  default     = "t3.large"
}

variable "k3s_version" {
  description = "Version de K3s"
  type        = string
  default     = "v1.35.8+k3s1"
}

module "compute" {
  source = "./modules/compute"

  project_name  = var.project_name
  vpc_id        = module.network.vpc_id
  subnet_id     = module.network.subnet_id
  admin_cidr    = var.admin_cidr
  public_key    = file(pathexpand(var.public_key_path))
  instance_type = var.instance_type
  k3s_version   = var.k3s_version

  depends_on = [module.network]
}

output "instance_id" {
  value = module.compute.instance_id
}

output "public_ip" {
  value = module.compute.public_ip
}

output "app_url" {
  value = "http://${module.compute.public_ip}"
}
