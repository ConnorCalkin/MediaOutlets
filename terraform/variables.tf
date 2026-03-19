variable "openai_api_key" {
    type      = string
    sensitive = true
}

variable "chroma_host" {
    type = string
}

variable "vpc_id" {
    description = "VPC ID"
    type        = string
    default = "vpc-03f0d39570fbaa750"
}

variable "chroma_port" {
    type    = number
    default = 8000
}