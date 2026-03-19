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