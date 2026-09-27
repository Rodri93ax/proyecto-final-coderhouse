terraform {
  backend "s3" {
    bucket       = "coderhouse-tfstate-277385996330-us-east-1"
    key          = "coderhouse/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
