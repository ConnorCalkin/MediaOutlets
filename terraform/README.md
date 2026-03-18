# Infrastructure

Terraform configuration for provisioning the DynamoDB table used to store scraped article data.

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) installed
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with `aws configure`

## Usage
```bash
terraform init
terraform plan
terraform apply
```

## Tear down
```bash
terraform destroy
```