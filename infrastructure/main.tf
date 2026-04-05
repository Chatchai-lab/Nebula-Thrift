# Nebula Thrift — Root Terraform Module
# Connects all infrastructure modules

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    # Remote state configuration — added in Phase 5
  }
}

provider "aws" {
  region = var.aws_region
}
