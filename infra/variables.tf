variable "aws_region" {
  description = "Region del laboratorio"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefijo de los recursos"
  type        = string
  default     = "coderhouse"
}

variable "vpc_cidr" {
  description = "Red privada del laboratorio"
  type        = string
  default     = "10.42.0.0/16"
}

variable "subnet_cidr" {
  description = "Subred para el servidor"
  type        = string
  default     = "10.42.1.0/24"
}
