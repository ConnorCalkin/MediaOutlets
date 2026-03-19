variable "vpc_id" {
    type = string
    default = "vpc-03f0d39570fbaa750"
}

variable "private_subnet_ids" {
    type = list(string)
    default = [
        "subnet-060cced5eb04380bf",
        "subnet-0fea0e0a59c4a45ad",
        "subnet-03d6ad56638c7aa28"
    ]
}

variable "public_subnet_ids" {
    type = list(string)
    default = [
        "subnet-0cfeaca0e941dea5b",
        "subnet-055ac264d45bec709",
        "subnet-046ec8b4e41d59ea8"
    ]
}

variable "aws_region" {
    type    = string
    default = "eu-west-2"
}

variable "openai_api_key" {
    type      = string
    sensitive = true
}

variable "chroma_host" {
    type = string
}

variable "chroma_port" {
    type    = number
    default = 8000
}

variable "image_uri" {
    type = string
}