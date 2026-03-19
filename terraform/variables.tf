variable "OPENAI_API_KEY" {
    description = "OpenAI API key for accessing the OpenAI services"
    type        = string
    sensitive   = true
}

variable "subnet_ids" {
    description = "List of subnet IDs for the ECS service"
    type        = list(string)
    default = [ "subnet-046ec8b4e41d59ea8", "subnet-060cced5eb04380bf" ]
}

variable "vpc_id" {
    description = "VPC ID"
    type        = string
    default = "vpc-03f0d39570fbaa750"
}

variable "CHROMA_HOST" {
    description = "Chroma host for the pipeline"
    type        = string
    default = ""
}