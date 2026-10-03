terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

data "aws_ami" "ubuntu" {
  owners = ["099720109477"]

  filter {
    name   = "image-id"
    values = ["ami-0045d7fc2ad003464"]
  }
}

resource "aws_key_pair" "this" {
  key_name   = "${var.project_name}-ssh"
  public_key = var.public_key
}

resource "aws_security_group" "this" {
  name_prefix = "${var.project_name}-"
  description = "Acceso al laboratorio K3s"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH desde la IP del administrador"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    description = "HTTP para la API de demostracion"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Salida para actualizaciones e imagenes"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

resource "aws_instance" "this" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.this.id]
  key_name                    = aws_key_pair.this.key_name
  iam_instance_profile        = aws_iam_instance_profile.ssm.name
  associate_public_ip_address = true
  monitoring                  = false

  user_data = templatefile("${path.module}/bootstrap.sh.tftpl", {
    k3s_version = var.k3s_version
  })
  user_data_replace_on_change = true

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    encrypted             = true
    delete_on_termination = true
  }

  credit_specification {
    cpu_credits = "standard"
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tags = {
    Name = "${var.project_name}-k3s"
  }

  volume_tags = {
    Name        = "${var.project_name}-root"
    Project     = var.project_name
    Environment = "lab"
    ManagedBy   = "Terraform"
  }
}
